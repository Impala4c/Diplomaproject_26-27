import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "src"))

from scripts.build_synthetic_history import git_command
from secret_history.cli import SafeArgumentParser
from secret_history.git_history.reader import git_environment
from secret_history.reporting.sarif import as_sarif
from secret_history.scanner import scan_repository
from tests.support import pair_text
from tests.unit.test_detectors import fake_pem, fake_token


def main():
    import jsonschema
    import yaml

    parser = SafeArgumentParser(description="Validate SARIF, workflow YAML and installed pre-commit in a temporary repository.")
    parser.add_argument("--schema", type=Path, required=True)
    args = parser.parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8-sig"))
    workflow = yaml.load((PROJECT / ".github/workflows/ci.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if set(workflow["jobs"]) != {"test", "scan"} or workflow["permissions"] != {"contents": "read"}:
        raise ValueError("Unexpected workflow configuration")
    temporary_root = (PROJECT / "tmp").resolve()
    temporary_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="integrations-", dir=temporary_root) as name:
        root = Path(name).resolve()
        if not root.is_relative_to(temporary_root):
            raise ValueError("Temporary directory escaped workspace")
        repository = root / "repo"
        repository.mkdir()
        git_command(repository, "init", "--template=", "--initial-branch=main")
        shutil.copytree(PROJECT / "src", repository / "src")
        (repository / "scripts").mkdir()
        shutil.copy2(PROJECT / "scripts/scan_history.py", repository / "scripts/scan_history.py")
        shutil.copy2(PROJECT / ".pre-commit-config.yaml", repository / ".pre-commit-config.yaml")
        (repository / ".env").write_text(pair_text(), encoding="utf-8")
        values = [fake_token(kind) for kind in ("github", "slack", "google")]
        (repository / "tokens.txt").write_text("\n".join(values) + "\n" + fake_pem(), encoding="utf-8")
        git_command(repository, "add", "--all")
        report = scan_repository(repository, detectors="all", mode="staged")
        sarif = as_sarif(report)
        jsonschema.validate(sarif, schema)
        if len(sarif["runs"][0]["results"]) != 5:
            raise ValueError("Unexpected SARIF result count")
        env = git_environment()
        env.update(PRE_COMMIT_HOME=str(root / "cache"), PYTHONDONTWRITEBYTECODE="1")
        env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
        commands = ([sys.executable, "-B", "-m", "pre_commit", "validate-config"],
                    [sys.executable, "-B", "-m", "pre_commit", "install", "--install-hooks"])
        for command in commands:
            completed = subprocess.run(command, cwd=repository, env=env, capture_output=True, timeout=60)
            if completed.returncode:
                raise ValueError("pre-commit preparation failed")
        git_args = ["git", "-c", "core.hooksPath=.git/hooks", "-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid",
                    "-c", "commit.gpgSign=false", "-C", str(repository), "commit", "-m", "Synthetic integration check"]
        blocked = subprocess.run(git_args, env=env, capture_output=True, timeout=60)
        if blocked.returncode == 0 or b"hook id: secret-history" not in blocked.stdout + blocked.stderr or any(value.encode() in blocked.stdout + blocked.stderr for value in values):
            raise ValueError("Hook did not block safely")
        (repository / ".env").write_text("APP_ENV=test\n", encoding="utf-8")
        (repository / "tokens.txt").write_text("clean\n", encoding="utf-8")
        git_command(repository, "add", "--all")
        clean = subprocess.run(git_args, env=env, capture_output=True, timeout=60)
        if clean.returncode:
            raise ValueError("Clean staged content did not pass hook")
        print(json.dumps({"sarif_official_schema": "OK", "workflow_yaml": "OK", "pre_commit_installed_hook": "OK",
                          "secret_commit": "blocked", "clean_commit": "accepted", "github_actions_remote_run": False}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("Integration verification failed. Check optional packages, schema and Git hook execution permissions.", file=sys.stderr)
        raise SystemExit(2)
