import contextlib
import io
import json
import logging
import subprocess
import sys
from unittest.mock import patch

from tests.support import PROJECT, RepositoryTest, pair_text, synthetic_pair
from tests.unit.test_detectors import fake_pem, fake_token
from secret_history.cli import main
from secret_history.git_history.reader import GitError, GitReader
from secret_history.reporting.report import as_csv, as_json
from secret_history.reporting.sarif import as_sarif
from secret_history.scanner import scan_repository


class PrivacyTests(RepositoryTest):
    def setUp(self):
        super().setUp()
        self.secrets = [*synthetic_pair("test-pair"), *(fake_token(kind) for kind in ("github", "slack", "google")), fake_pem().splitlines()[1]]
        self.write(".env", pair_text())
        self.write("example.txt", "\n".join(self.secrets[2:5]) + "\n" + fake_pem())
        self.commit()

    def assert_private(self, output):
        for secret in self.secrets:
            self.assertNotIn(secret, output)

    def test_json_csv_sarif_stdout_stderr_and_logging(self):
        out, err, logs = io.StringIO(), io.StringIO(), io.StringIO()
        handler = logging.StreamHandler(logs)
        logging.getLogger().addHandler(handler)
        self.addCleanup(logging.getLogger().removeHandler, handler)
        paths = [self.root / ("result." + ext) for ext in ("json", "csv", "sarif")]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main([str(self.repo), "--output", str(paths[0]), "--csv", str(paths[1]), "--sarif", str(paths[2])])
        self.assertEqual(code, 1)
        self.assertEqual(len(json.loads(paths[2].read_text())["runs"][0]["results"]), 5)
        self.assert_private(out.getvalue() + err.getvalue() + logs.getvalue() + "".join(p.read_text() for p in paths))
        result = subprocess.run([sys.executable, "-B", str(PROJECT / "scripts/scan_history.py"), str(self.repo)], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 1)
        self.assert_private(result.stdout + result.stderr)

    def test_secret_in_candidate_and_skipped_paths_is_masked(self):
        token = fake_token("github")
        self.write(token + "/.env", pair_text())
        self.write(token + "/binary", b"\0")
        self.commit()
        report = scan_repository(self.repo, detectors="all")
        self.assert_private(as_json(report) + as_csv(report) + as_json(as_sarif(report)))
        self.assertTrue(any("[REDACTED]" in row["path"] for row in report["candidates"]))

    def test_errors_never_forward_exception_payload_or_traceback(self):
        for exception in (GitError(self.secrets[0]), OSError(self.secrets[1]), ValueError(self.secrets[2]), RuntimeError(self.secrets[3])):
            out, err = io.StringIO(), io.StringIO()
            with patch("secret_history.cli.scan_repository", side_effect=exception), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(main([str(self.repo)]), 2)
            self.assert_private(out.getvalue() + err.getvalue())
            self.assertNotIn("Traceback", err.getvalue())

    def test_invalid_cli_arguments_paths_and_values_are_not_echoed(self):
        cases = [[str(self.repo), "--unknown=" + self.secrets[0]],
                 [str(self.repo), "--max-blob-bytes", self.secrets[1]],
                 [str(self.root / self.secrets[2])],
                 [str(self.repo), "--ref", self.secrets[3]],
                 [str(self.repo), "--detectors", self.secrets[4]]]
        for argv in cases:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    code = main(argv)
                except SystemExit as exc:
                    code = exc.code
            self.assertEqual(code, 2)
            self.assert_private(out.getvalue() + err.getvalue())

    def test_git_stderr_and_timeout_payload_are_suppressed(self):
        payload = self.secrets[2].encode()
        reader = GitReader(self.repo)
        result = subprocess.CompletedProcess([], 1, stdout=payload, stderr=payload)
        for failure in (result, subprocess.TimeoutExpired("git", 30, output=payload, stderr=payload)):
            kwargs = {"side_effect": failure} if isinstance(failure, Exception) else {"return_value": failure}
            with patch("secret_history.git_history.reader.subprocess.run", **kwargs):
                with self.assertRaises(GitError) as raised:
                    reader.blob("a" * 40)
            self.assert_private(str(raised.exception))

    def test_report_write_failure_does_not_echo_destination(self):
        err = io.StringIO()
        with patch("pathlib.Path.open", side_effect=OSError(self.secrets[1])), contextlib.redirect_stderr(err):
            self.assertEqual(main([str(self.repo), "--output", str(self.root / "result.json")]), 2)
        self.assert_private(err.getvalue())
