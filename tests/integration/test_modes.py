import contextlib
import io
import json
import os
import shutil
from unittest.mock import patch

from tests.support import RepositoryTest, git_command, pair_text
from tests.unit.test_detectors import fake_token
from secret_history.cli import main
from secret_history.git_history.reader import GitError, GitReader
from secret_history.reporting.sarif import as_sarif
from secret_history.scanner import scan_repository


class ModeTests(RepositoryTest):
    def test_explicit_exclusion_changes_scope_and_does_not_hide_other_alerts(self):
        self.write("docs/plan.pdf", b"\0")
        self.write("docs/token.txt", fake_token("github"))
        self.commit()
        excluded = scan_repository(self.repo, detectors="all", exclude=["docs/*.pdf"])
        self.assertTrue(excluded["coverage"]["complete_for_scope"])
        self.assertEqual(excluded["summary"]["alerts"], 1)
        self.assertEqual(excluded["scope"]["excluded_path_globs"], ["docs/*.pdf"])
        self.assertEqual(excluded["coverage"]["out_of_scope_file_occurrences"], 1)
        self.assertFalse(scan_repository(self.repo, detectors="all")["coverage"]["complete_for_scope"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.repo), "--exclude", "docs/*.pdf"]), 1)

    def test_staged_respects_git_hook_alternate_index_but_history_is_isolated(self):
        self.write("token.txt", "clean")
        self.commit()
        alternate = self.repo / ".git" / "alternate-index"
        shutil.copy2(self.repo / ".git" / "index", alternate)
        self.write("token.txt", fake_token("github"))
        git_command(self.repo, "add", "--all")
        self.assertEqual(scan_repository(self.repo, mode="staged", detectors="all")["summary"]["alerts"], 1)
        with patch.dict(os.environ, {"GIT_INDEX_FILE": str(alternate)}):
            self.assertEqual(scan_repository(self.repo, mode="staged", detectors="all")["summary"]["alerts"], 0)
            self.assertEqual(scan_repository(self.repo, detectors="all")["summary"]["alerts"], 0)
        with patch.dict(os.environ, {"GIT_INDEX_FILE": str(self.root / "outside-index")}):
            with self.assertRaises(GitError):
                scan_repository(self.repo, mode="staged", detectors="all")

    def test_staged_unborn_index_does_not_read_worktree(self):
        self.write("token.txt", fake_token("github"))
        git_command(self.repo, "add", "--all")
        self.write("token.txt", "clean uncommitted worktree")
        report = scan_repository(self.repo, mode="staged", detectors="all")
        self.assertEqual(report["summary"]["alerts"], 1)
        self.assertTrue(report["reference_snapshot_oid"].startswith("index:"))
        self.assertEqual(report, scan_repository(self.repo, mode="staged", detectors="all"))

    def test_unstaged_secret_is_not_part_of_staged_content(self):
        self.write("token.txt", "clean")
        git_command(self.repo, "add", "--all")
        self.write("token.txt", fake_token("github"))
        self.assertEqual(scan_repository(self.repo, mode="staged", detectors="all")["summary"]["alerts"], 0)

    def test_staged_only_checks_changed_files_and_handles_deletions(self):
        self.write("token.txt", fake_token("github"))
        self.commit()
        self.write("readme.txt", "clean")
        git_command(self.repo, "add", "readme.txt")
        self.assertEqual(scan_repository(self.repo, mode="staged", detectors="all")["summary"]["alerts"], 0)
        git_command(self.repo, "rm", "token.txt")
        self.assertEqual(scan_repository(self.repo, mode="staged", detectors="all")["summary"]["alerts"], 0)

    def test_index_conflicts_fail_closed(self):
        self.write("f.txt", "initial")
        self.commit()
        git_command(self.repo, "checkout", "-b", "feature")
        self.write("f.txt", "feature")
        self.commit()
        git_command(self.repo, "checkout", "main")
        self.write("f.txt", "main")
        self.commit()
        try:
            git_command(self.repo, "merge", "feature")
        except Exception:
            pass
        with self.assertRaises(GitError):
            scan_repository(self.repo, mode="staged", detectors="all")

    def test_snapshot_history_limit_and_all_refs(self):
        self.write("readme.txt", "clean")
        self.commit()
        git_command(self.repo, "checkout", "-b", "feature")
        self.write("token.txt", fake_token("github"))
        self.commit()
        git_command(self.repo, "checkout", "main")
        self.assertEqual(scan_repository(self.repo, detectors="all")["summary"]["alerts"], 0)
        self.assertEqual(scan_repository(self.repo, detectors="all", all_refs=True)["summary"]["alerts"], 1)
        self.write(".env", pair_text())
        self.commit()
        self.write(".env", "clean")
        self.commit()
        self.assertEqual(scan_repository(self.repo, mode="snapshot")["summary"]["alerts"], 0)
        limited = scan_repository(self.repo, max_commits=1)
        self.assertTrue(limited["coverage"]["history_truncated"])
        self.assertFalse(limited["coverage"]["complete_for_scope"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.repo), "--max-commits", "1"]), 2)

    def test_blob_cache_accounts_for_rename_into_env_scope(self):
        self.write("credentials.txt", pair_text())
        self.commit()
        git_command(self.repo, "mv", "credentials.txt", ".env")
        self.commit()
        report = scan_repository(self.repo, detectors="all")
        self.assertEqual(report["summary"]["alerts"], 1)
        self.assertEqual(report["coverage"]["unique_blobs_read"], 1)

    def test_batch_reader_respects_size_limit_and_preserves_binary_bytes(self):
        for index in range(70):
            self.write(f"file{index}.txt", bytes([index]) * (100 if index != 4 else 5000))
        self.commit()
        reader = GitReader(self.repo)
        entries = reader.entries(reader.resolve("HEAD"))
        values = reader.read_blobs([e.oid for e in entries], 1024)
        for entry in entries:
            index = int(entry.path[4:-4])
            self.assertEqual(values[entry.oid], None if index == 4 else bytes([index]) * 100)

    def test_sarif_locations_fingerprints_coverage_and_negative_filter(self):
        self.write("a b/token.txt", fake_token("github"))
        self.write(".env", "AWS_ACCESS_KEY_ID=\nAWS_SECRET_ACCESS_KEY=\n")
        self.commit()
        report = scan_repository(self.repo, detectors="all")
        sarif = as_sarif(report)
        run = sarif["runs"][0]
        self.assertEqual(sarif["version"], "2.1.0")
        self.assertEqual(len(run["results"]), 1)
        result = run["results"][0]
        self.assertEqual(result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"], "a%20b/token.txt")
        self.assertIn(result["partialFingerprints"]["secretHistory/location-v1"], [r["fingerprint"] for r in report["candidates"]])
        self.write("binary", b"\0")
        self.commit()
        incomplete = as_sarif(scan_repository(self.repo, detectors="all"))["runs"][0]["invocations"][0]
        self.assertFalse(incomplete["executionSuccessful"])
        self.assertIn("toolExecutionNotifications", incomplete)
