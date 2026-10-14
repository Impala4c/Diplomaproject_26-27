import argparse
from pathlib import Path
import sys

from secret_history.reporting.report import as_csv, as_json
from secret_history.reporting.sarif import as_sarif
from secret_history.scanner import scan_repository


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, "Error: invalid arguments or output destination; use --help.\n")


def main(argv: list[str] | None = None) -> int:
    parser = SafeArgumentParser(prog="secret-history", description="Scan local Git blobs without exporting credential values.")
    parser.add_argument("repository", type=Path)
    parser.add_argument("--ref", default="HEAD", help="Commit or branch to scan")
    parser.add_argument("--git", default="git", help="Git executable")
    parser.add_argument("--detectors", default="all", help="all or comma-separated aws,github,pem,slack,google")
    parser.add_argument("--exclude", action="append", default=[], help="Explicit case-sensitive path glob outside scan scope; use / and repeat as needed")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--snapshot", action="store_true", help="Scan only the selected commit")
    modes.add_argument("--staged", action="store_true", help="Scan changed staged files, including before the first commit")
    parser.add_argument("--all-refs", action="store_true", help="Include all locally available refs")
    parser.add_argument("--max-commits", type=int, help="Bound history; truncated scans exit with code 2")
    parser.add_argument("--max-blob-bytes", type=int, default=1_048_576)
    parser.add_argument("--output", type=Path, help="New JSON file; existing files are never overwritten")
    parser.add_argument("--csv", type=Path, help="New CSV file; requires --output")
    parser.add_argument("--sarif", type=Path, help="New SARIF file; requires --output for full coverage metadata")
    args = parser.parse_args(argv)
    if args.max_blob_bytes <= 0 or (args.max_commits is not None and args.max_commits <= 0):
        parser.error("Limits must be positive")
    if (args.csv or args.sarif) and not args.output:
        parser.error("Companion JSON is required")
    if (args.snapshot or args.staged) and (args.all_refs or args.max_commits):
        parser.error("Incompatible modes")
    try:
        outputs = [path for path in (args.output, args.csv, args.sarif) if path is not None]
        if len({path.resolve() for path in outputs}) != len(outputs) or any(path.exists() for path in outputs):
            parser.error("Output destinations must be new and distinct")
        mode = "staged" if args.staged else "snapshot" if args.snapshot else "history"
        report = scan_repository(args.repository, args.ref, git=args.git, max_blob_bytes=args.max_blob_bytes,
                                 detectors=args.detectors, mode=mode, all_refs=args.all_refs, max_commits=args.max_commits, exclude=args.exclude)
        if args.output:
            for path, content in ((args.output, as_json(report)), (args.csv, as_csv(report)), (args.sarif, as_json(as_sarif(report)))):
                if path is not None:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("x", encoding="utf-8", newline="") as handle:
                        handle.write(content)
            print(as_json({"summary": report["summary"], "complete_for_scope": report["coverage"]["complete_for_scope"]}), end="")
        else:
            print(as_json(report), end="")
    except KeyboardInterrupt:
        print("Error: scan interrupted.", file=sys.stderr)
        return 130
    except Exception:
        print("Error: scan or report write failed. Check repository, ref, limits and permissions.", file=sys.stderr)
        return 2
    if not report["coverage"]["complete_for_scope"]:
        return 2
    return 1 if report["summary"]["alerts"] else 0
