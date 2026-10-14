from pathlib import Path
import shlex
import sys

from tests.support import PROJECT, RepositoryTest, git_command
from tests.unit.test_detectors import fake_token


class HookTests(RepositoryTest):
    def test_real_git_pre_commit_blocks_secret_and_allows_clean_index(self):
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        hook.parent.mkdir(exist_ok=True)
        executable = shlex.quote(Path(sys.executable).as_posix())
        script = shlex.quote((PROJECT / "scripts/scan_history.py").as_posix())
        hook.write_text(f"#!/bin/sh\nexec {executable} -B {script} . --staged --detectors all\n", encoding="utf-8", newline="\n")
        hook.chmod(0o755)
        self.write("token.txt", fake_token("github"))
        git_command(self.repo, "add", "--all")
        with self.assertRaises(RuntimeError):
            git_command(self.repo, "-c", "core.hooksPath=.git/hooks", "commit", "-m", "Must be blocked")
        self.write("token.txt", "clean")
        git_command(self.repo, "add", "--all")
        git_command(self.repo, "-c", "core.hooksPath=.git/hooks", "commit", "-m", "Clean index passes")
        self.assertEqual(git_command(self.repo, "rev-list", "--count", "HEAD"), "1")
        self.write("other.txt", "clean separate file")
        git_command(self.repo, "add", "--all")
        git_command(self.repo, "commit", "-m", "Prepare partial commit")
        self.write("other.txt", "clean change")
        self.write("token.txt", fake_token("github"))
        git_command(self.repo, "add", "--all")
        git_command(self.repo, "-c", "core.hooksPath=.git/hooks", "commit", "--only", "other.txt", "-m", "Clean partial commit passes")
        with self.assertRaises(RuntimeError):
            git_command(self.repo, "-c", "core.hooksPath=.git/hooks", "commit", "--only", "token.txt", "-m", "Secret partial commit blocks")
        self.assertEqual(git_command(self.repo, "rev-list", "--count", "HEAD"), "3")
