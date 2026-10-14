from pathlib import Path
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from scripts.build_synthetic_history import git_command, synthetic_pair


def pair_text(seed: str = "test-pair") -> str:
    identifier, secret = synthetic_pair(seed)
    return f"AWS_ACCESS_KEY_ID={identifier}\nAWS_SECRET_ACCESS_KEY={secret}\n"


class RepositoryTest(unittest.TestCase):
    def setUp(self):
        test_root = (PROJECT / "tmp").resolve()
        test_root.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="aws-test-", dir=test_root)
        self.root = Path(self.temporary.name).resolve()
        if not self.root.is_relative_to(test_root):
            raise RuntimeError("Temporary test path escaped workspace tmp directory")
        self.addCleanup(self.temporary.cleanup)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git_command(self.repo, "init", "--template=", "--initial-branch=main")

    def write(self, name: str, content: str | bytes):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")

    def commit(self, message: str = "Synthetic fixture") -> str:
        git_command(self.repo, "add", "--all")
        git_command(self.repo, "commit", "--allow-empty", "-m", message)
        return git_command(self.repo, "rev-parse", "HEAD")
