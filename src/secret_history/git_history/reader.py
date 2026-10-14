from dataclasses import dataclass
import os
from pathlib import Path
import subprocess


class GitError(RuntimeError):
    pass


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    object_type: str
    oid: str
    path: str


def git_environment() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
    })
    return env


class GitReader:
    def __init__(self, repository: Path, git: str = "git", timeout: float = 30):
        self.repository = repository.resolve()
        self.git = git
        self.timeout = timeout
        self.index_path = None
        if not self.repository.is_dir():
            raise GitError("Repository directory does not exist.")
        if not ((self.repository / ".git").exists() or
                ((self.repository / "HEAD").is_file() and (self.repository / "objects").is_dir())):
            raise GitError("Pass the root of a local Git repository.")

    def run(self, *args: str, input_data: bytes | None = None) -> bytes:
        command = [self.git, "-c", "protocol.allow=never", "-c", "core.fsmonitor=false",
                   "-c", f"core.hooksPath={os.devnull}", "-C", str(self.repository), *args]
        env = git_environment()
        if self.index_path is not None:
            env["GIT_INDEX_FILE"] = str(self.index_path)
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=env, timeout=self.timeout, check=False, input=input_data)
        except FileNotFoundError as exc:
            raise GitError("Git executable was not found.") from exc
        except subprocess.TimeoutExpired as exc:
            raise GitError("Git command timed out; scan did not complete.") from exc
        except OSError as exc:
            raise GitError("Cannot start Git.") from exc
        if result.returncode:
            raise GitError(f"Git {args[0]} failed; check repository objects and selected ref.")
        return result.stdout

    def resolve(self, ref: str) -> str:
        if self.run("rev-parse", "--is-shallow-repository").strip() == b"true":
            raise GitError("Shallow repositories are not supported; history would be incomplete.")
        return self.run("rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").decode("ascii").strip()

    def commits(self, oid: str) -> list[str]:
        return self.run("rev-list", "--topo-order", "--reverse", oid, "--").decode("ascii").splitlines()

    def entries(self, commit: str) -> list[TreeEntry]:
        result = []
        for record in self.run("ls-tree", "-r", "-z", commit).split(b"\0"):
            if not record:
                continue
            metadata, path = record.split(b"\t", 1)
            mode, object_type, oid = metadata.decode("ascii").split()
            result.append(TreeEntry(mode, object_type, oid, path.decode("utf-8", "surrogateescape")))
        return result

    def blob_size(self, oid: str) -> int:
        return int(self.run("cat-file", "-s", oid))

    def blob(self, oid: str) -> bytes:
        return self.run("cat-file", "blob", oid)

    def read_blobs(self, oids: list[str], max_bytes: int) -> dict[str, bytes | None]:
        result = {}
        for start in range(0, len(oids), 64):
            chunk = oids[start:start + 64]
            if len(chunk) == 1:
                oid = chunk[0]
                result[oid] = self.blob(oid) if self.blob_size(oid) <= max_bytes else None
                continue
            payload = ("\n".join(chunk) + "\n").encode("ascii")
            headers = self.run("cat-file", "--batch-check", input_data=payload).splitlines()
            selected = []
            for expected, header in zip(chunk, headers, strict=True):
                parts = header.decode("ascii").split()
                if len(parts) != 3 or parts[0] != expected or parts[1] != "blob":
                    raise GitError("Cannot read requested Git blob.")
                if int(parts[2]) > max_bytes:
                    result[expected] = None
                else:
                    selected.append(expected)
            if not selected:
                continue
            data = self.run("cat-file", "--batch", input_data=("\n".join(selected) + "\n").encode("ascii"))
            offset = 0
            for expected in selected:
                end = data.index(b"\n", offset)
                oid, kind, size = data[offset:end].decode("ascii").split()
                size = int(size)
                if oid != expected or kind != "blob" or size > max_bytes:
                    raise GitError("Unexpected Git blob response.")
                result[oid] = data[end + 1:end + 1 + size]
                offset = end + size + 2
                if len(result[oid]) != size:
                    raise GitError("Truncated Git blob response.")
        return result

    def all_commits(self) -> list[str]:
        return self.run("rev-list", "--topo-order", "--reverse", "--all", "--").decode("ascii").splitlines()

    def staged_entries(self) -> list[TreeEntry]:
        inherited_index = os.environ.get("GIT_INDEX_FILE")
        if inherited_index:
            git_dir = Path(self.run("rev-parse", "--absolute-git-dir").decode("utf-8").strip()).resolve()
            index_path = Path(inherited_index)
            if not index_path.is_absolute():
                index_path = self.repository / index_path
            index_path = index_path.resolve()
            if not index_path.is_relative_to(git_dir):
                raise GitError("Inherited index must reside inside this repository Git directory.")
            self.index_path = index_path
        changed = set(self.run("diff", "--cached", "--name-only", "--no-ext-diff", "--no-textconv", "-z", "--diff-filter=ACMRTU").split(b"\0"))
        entries = []
        for record in self.run("ls-files", "--stage", "-z").split(b"\0"):
            if not record:
                continue
            metadata, path = record.split(b"\t", 1)
            mode, oid, stage = metadata.decode("ascii").split()
            if stage != "0":
                raise GitError("Resolve index conflicts before scanning staged files.")
            if path in changed:
                entries.append(TreeEntry(mode, "commit" if mode == "160000" else "blob", oid, path.decode("utf-8", "surrogateescape")))
        return entries
