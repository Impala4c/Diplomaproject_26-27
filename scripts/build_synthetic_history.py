
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from secret_history.git_history.reader import git_environment


def synthetic_pair(seed: str = "aws-history-demo-v1") -> tuple[str, str]:
    identifier = "AKIA" + base64.b32encode(hashlib.sha256(seed.encode()).digest()).decode()[:16]
    secret = base64.b64encode(hashlib.sha256((seed + ":secret").encode()).digest()[:30]).decode()
    return identifier, secret


def git_command(repository: Path, *args: str, git: str = "git") -> str:
    result = subprocess.run(
        [git, "-c", "core.hooksPath=", "-c", "core.autocrlf=false", "-c", "commit.gpgSign=false",
         "-c", "user.name=Synthetic Demo", "-c", "user.email=synthetic@example.invalid",
         "-C", str(repository), *args], env=git_environment(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Git {args[0]} failed while building the synthetic history.")
    return result.stdout.decode("utf-8", "replace").strip()


def build_history(destination: Path, git: str = "git") -> dict:
    destination = destination.resolve()
    if destination.exists():
        raise ValueError("Destination already exists; use a new directory. Nothing was overwritten.")
    destination.mkdir(parents=True)
    git_command(destination, "init", "--template=", "--initial-branch=main", git=git)
    (destination / "README.md").write_text(
        "# Synthetic AWS history\n\nAll credentials in this history are generated test strings.\n"
        "They were never created in an AWS account. No online verification is needed.\n",
        encoding="utf-8",
    )
    env_file = destination / ".env"
    clean = "APP_ENV=development\n"
    env_file.write_text(clean, encoding="utf-8")
    git_command(destination, "add", "--", "README.md", ".env", git=git)
    git_command(destination, "commit", "-m", "Initial configuration without credentials", git=git)
    initial = git_command(destination, "rev-parse", "HEAD", git=git)
    identifier, secret = synthetic_pair()
    env_file.write_text(clean + f"AWS_ACCESS_KEY_ID={identifier}\nAWS_SECRET_ACCESS_KEY={secret}\n", encoding="utf-8")
    git_command(destination, "add", "--", ".env", git=git)
    git_command(destination, "commit", "-m", "Add synthetic AWS pair", git=git)
    added = git_command(destination, "rev-parse", "HEAD", git=git)
    env_file.write_text(clean, encoding="utf-8")
    git_command(destination, "add", "--", ".env", git=git)
    git_command(destination, "commit", "-m", "Remove synthetic AWS pair", git=git)
    removed = git_command(destination, "rev-parse", "HEAD", git=git)
    return {"repository": str(destination), "synthetic": True,
            "commits": {"initial": initial, "pair_added": added, "pair_removed": removed},
            "expected": {"path": ".env", "line_start": 2, "line_end": 3,
                         "suspected_pair_records": 1, "absent_from_reference_env": True}}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local history with never-issued synthetic AWS credentials.")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--git", default="git")
    args = parser.parse_args()
    try:
        result = build_history(args.destination, args.git)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(str(exc) if isinstance(exc, (ValueError, RuntimeError)) else "Cannot build synthetic history.", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
