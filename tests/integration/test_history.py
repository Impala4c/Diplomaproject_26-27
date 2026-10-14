import contextlib
import io
import json
import subprocess
import sys
from unittest.mock import patch

from tests.support import PROJECT, RepositoryTest, git_command, pair_text, synthetic_pair
from scripts.build_synthetic_history import build_history
from secret_history.cli import main
from secret_history.git_history.reader import GitError, GitReader
from secret_history.reporting.report import as_csv, as_json
from secret_history.scanner import scan_repository


class HistoryTests(RepositoryTest):
    def test_three_commit_demo_deleted_pair_and_masking(self):
        manifest = build_history(self.root / "demo")
        report = scan_repository(self.root / "demo")
        self.assertEqual(report["coverage"]["commits_scanned"], 3)
        self.assertEqual(report["summary"]["decisions"], {"SUSPECTED_SECRET": 1})
        row = report["candidates"][0]
        self.assertEqual(row["commits"], [manifest["commits"]["pair_added"]])
        self.assertEqual((row["line_start"], row["line_end"]), (2, 3))
        self.assertTrue(row["absent_from_reference_env"])
        self.assertFalse(row["location_in_reference_snapshot"])
        for value in synthetic_pair():
            self.assertNotIn(value, as_json(report))
            self.assertNotIn(value, as_csv(report))

    def test_initial_commit_repeated_blob_and_untouched_worktree(self):
        self.write(".env", pair_text())
        initial = self.commit()
        second = self.commit()
        self.write(".env", "LOCAL_UNCOMMITTED_CHANGE=1\n")
        before = git_command(self.repo, "status", "--porcelain")
        report = scan_repository(self.repo)
        self.assertEqual(report["coverage"]["unique_env_blobs_read"], 1)
        self.assertEqual([row["commits"] for row in report["candidates"]], [[initial], [second]])
        self.assertEqual([row["commit_oid"] for row in report["candidates"]], [initial, second])
        self.assertEqual(len({row["fingerprint"] for row in report["candidates"]}), 2)
        self.assertTrue(all(row["location_in_reference_snapshot"] for row in report["candidates"]))
        self.assertFalse(report["candidates"][0]["absent_from_reference_env"])
        self.assertEqual(git_command(self.repo, "status", "--porcelain"), before)
        self.assertEqual((self.repo / ".env").read_text(), "LOCAL_UNCOMMITTED_CHANGE=1\n")

    def test_rename_and_same_content_different_paths(self):
        self.write("old/.env", pair_text())
        self.commit()
        git_command(self.repo, "mv", "old", "new")
        self.write("copy/.env.example", pair_text())
        self.commit()
        report = scan_repository(self.repo)
        self.assertEqual(report["coverage"]["unique_env_blobs_read"], 1)
        self.assertEqual(len(report["candidates"]), 3)
        self.assertEqual(len({row["fingerprint"] for row in report["candidates"]}), 3)
        self.assertTrue(all(row["absent_from_reference_env"] is False for row in report["candidates"]))

    def test_unmerged_branch_excluded_and_merged_history_included(self):
        self.write("README.md", "Initial\n")
        self.commit()
        git_command(self.repo, "checkout", "-b", "feature")
        self.write(".env", pair_text())
        added = self.commit()
        self.write(".env", "APP_ENV=test\n")
        self.commit()
        git_command(self.repo, "checkout", "main")
        self.assertEqual(scan_repository(self.repo)["summary"]["alerts"], 0)
        git_command(self.repo, "merge", "--no-ff", "feature", "-m", "Merge synthetic history")
        report = scan_repository(self.repo)
        self.assertEqual(report["candidates"][0]["commits"], [added])
        self.assertTrue(report["candidates"][0]["absent_from_reference_env"])

    def test_components_in_different_commits_are_not_paired(self):
        identifier, secret = synthetic_pair()
        self.write(".env", f"AWS_ACCESS_KEY_ID={identifier}\n")
        self.commit()
        self.write(".env", f"AWS_SECRET_ACCESS_KEY={secret}\n")
        self.commit()
        rows = scan_repository(self.repo)["candidates"]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["kind"] == "aws_component" for row in rows))

    def test_scope_and_negative_examples(self):
        self.write("secrets.txt", pair_text())
        self.write(".env.example", "AWS_ACCESS_KEY_ID=your_access_key_here\nAWS_SECRET_ACCESS_KEY=your_secret_key_here\n")
        self.commit()
        report = scan_repository(self.repo)
        self.assertEqual(report["summary"]["alerts"], 0)
        self.assertEqual(report["summary"]["candidate_records"], 1)
        self.assertEqual(report["coverage"]["out_of_scope_file_occurrences"], 1)

    def test_binary_encoding_size_and_syntax_skips_are_visible(self):
        self.write(".env", pair_text())
        self.commit()
        self.write(".env", b"\xff\xfeinvalid")
        self.write(".env.binary", b"A\0B")
        self.write(".env.big", "A" * 2048)
        self.write(".env.syntax", 'AWS_SECRET_ACCESS_KEY="unclosed\n')
        self.commit()
        report = scan_repository(self.repo, max_blob_bytes=1024)
        reasons = {row["reason"] for row in report["coverage"]["skipped"]}
        self.assertEqual(reasons, {"non_utf8_not_supported", "binary_or_utf16_not_supported", "blob_size_limit"})
        self.assertFalse(report["coverage"]["complete_for_scope"])
        self.assertIsNone(report["candidates"][0]["absent_from_reference_env"])
        self.assertEqual(len(report["coverage"]["parse_warnings"]), 1)

    def test_component_still_present_when_it_becomes_a_pair(self):
        _, secret = synthetic_pair("test-pair")
        self.write(".env", f"AWS_SECRET_ACCESS_KEY={secret}\n")
        self.commit()
        self.write(".env", pair_text())
        self.commit()
        rows = scan_repository(self.repo)["candidates"]
        self.assertEqual(rows[0]["kind"], "aws_component")
        self.assertFalse(rows[0]["absent_from_reference_env"])

    def test_secret_like_text_in_comments_and_formula_path_is_not_exported(self):
        self.write("=1+2/.env", pair_text() + "# PRIVATE_COMMENT_MUST_NOT_LEAK\n")
        self.commit()
        report = scan_repository(self.repo)
        self.assertNotIn("PRIVATE_COMMENT_MUST_NOT_LEAK", as_json(report) + as_csv(report))
        import csv
        row = next(csv.DictReader(io.StringIO(as_csv(report))))
        self.assertEqual(row["path_json"], '"=1+2/.env"')

    def test_symlink_env_is_skipped_without_following_target(self):
        self.write("payload.txt", pair_text())
        self.commit()
        self.write("link-target", "payload.txt")
        oid = git_command(self.repo, "hash-object", "-w", "link-target")
        git_command(self.repo, "update-index", "--add", "--cacheinfo", f"120000,{oid},.env")
        git_command(self.repo, "commit", "-m", "Synthetic symlink")
        report = scan_repository(self.repo)
        self.assertEqual(report["coverage"]["skipped"][0]["reason"], "non_regular_env_file")
        self.assertEqual(report["summary"]["candidate_records"], 0)

    def test_submodule_is_reported_as_unscanned(self):
        self.write("README.md", "Synthetic submodule fixture\n")
        oid = self.commit()
        git_command(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{oid},vendor")
        git_command(self.repo, "commit", "-m", "Synthetic gitlink")
        report = scan_repository(self.repo)
        self.assertEqual(report["coverage"]["skipped"][0]["reason"], "submodule_not_scanned")
        self.assertFalse(report["coverage"]["complete_for_scope"])

    def test_lfs_pointer_is_not_a_clean_result(self):
        self.write(".env", "version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 999\n")
        self.commit()
        report = scan_repository(self.repo)
        self.assertFalse(report["coverage"]["complete_for_scope"])
        self.assertEqual(report["coverage"]["skipped"][0]["reason"], "lfs_pointer_not_resolved")

    def test_missing_ref_empty_repo_and_shallow_history_fail(self):
        with self.assertRaises(GitError):
            scan_repository(self.repo)
        self.write(".env", "APP_ENV=test\n")
        commit = self.commit()
        with self.assertRaises(GitError):
            scan_repository(self.repo, "missing-ref")
        (self.repo / ".git" / "shallow").write_text(commit + "\n", encoding="ascii")
        with self.assertRaisesRegex(GitError, "Shallow"):
            scan_repository(self.repo)

    def test_git_failure_does_not_return_a_clean_report(self):
        self.write(".env", pair_text())
        self.commit()
        with patch.object(GitReader, "blob", side_effect=GitError("Cannot read object")):
            with self.assertRaises(GitError):
                scan_repository(self.repo)

    def test_fingerprint_is_stable_across_scans(self):
        self.write(".env", pair_text())
        self.commit()
        first = scan_repository(self.repo)
        second = scan_repository(self.repo)
        self.assertEqual(first["candidates"][0]["fingerprint"], second["candidates"][0]["fingerprint"])
        self.assertEqual(as_json(first), as_json(second))
        self.assertEqual(as_csv(first), as_csv(second))
        self.assertEqual(first["fingerprint"]["algorithm"], "SHA-256")
        self.assertFalse(first["fingerprint"]["raw_values_included"])

    def test_fingerprints_are_stable_across_cli_processes(self):
        self.write(".env", pair_text())
        self.commit()
        command = [sys.executable, "-B", str(PROJECT / "scripts" / "scan_history.py"), str(self.repo)]
        first = subprocess.run(command, capture_output=True, text=True, timeout=60)
        second = subprocess.run(command, capture_output=True, text=True, timeout=60)
        self.assertEqual((first.returncode, second.returncode), (1, 1))
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual((first.stderr, second.stderr), ("", ""))

    def test_same_masked_values_at_different_locations_get_different_fingerprints(self):
        self.write("one/.env", pair_text())
        self.write("two/.env", pair_text("second-pair"))
        self.write("three/.env", pair_text() + pair_text("third-pair"))
        first_commit = self.commit()
        self.write("one/.env", pair_text("replacement"))
        self.commit()
        report = scan_repository(self.repo)
        rows = report["candidates"]
        self.assertEqual(len(rows), 12)
        self.assertEqual(len({row["fingerprint"] for row in rows}), len(rows))
        previous = scan_repository(self.repo, first_commit)
        self.assertEqual([row["fingerprint"] for row in previous["candidates"]],
                         [row["fingerprint"] for row in rows if row["commit_oid"] == first_commit])

    def test_new_commits_do_not_change_existing_occurrence_fingerprints(self):
        self.write(".env", pair_text())
        initial = self.commit()
        first = scan_repository(self.repo)
        self.commit()
        second = scan_repository(self.repo)
        self.assertEqual(len(second["candidates"]), 2)
        old = next(row for row in second["candidates"] if row["commit_oid"] == initial)
        self.assertEqual(first["candidates"][0]["fingerprint"], old["fingerprint"])
        self.assertEqual(len({row["fingerprint"] for row in second["candidates"]}), 2)

    def test_cli_json_csv_and_exit_codes(self):
        self.write(".env", pair_text())
        self.commit()
        output, csv_output = self.root / "report.json", self.root / "report.csv"
        command = [sys.executable, "-B", str(PROJECT / "scripts" / "scan_history.py"), str(self.repo),
                   "--output", str(output), "--csv", str(csv_output)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(output.read_text())["summary"]["alerts"], 1)
        for value in synthetic_pair("test-pair"):
            self.assertNotIn(value, output.read_text() + csv_output.read_text() + result.stdout + result.stderr)
        before = output.read_bytes()
        again = subprocess.run(command, capture_output=True, text=True, timeout=60)
        self.assertEqual(again.returncode, 2)
        self.assertEqual(output.read_bytes(), before)

    def test_clean_cli_returns_zero_and_incomplete_returns_two(self):
        self.write(".env", "AWS_ACCESS_KEY_ID=\nAWS_SECRET_ACCESS_KEY=\n")
        self.commit()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.repo)]), 0)
        self.write(".env", b"\0")
        self.commit()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.repo)]), 2)

    def test_demo_refuses_to_overwrite_existing_directory(self):
        self.write("keep.txt", "keep")
        with self.assertRaises(ValueError):
            build_history(self.repo)
        self.assertEqual((self.repo / "keep.txt").read_text(), "keep")
