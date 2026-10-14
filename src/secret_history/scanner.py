from collections import Counter
from fnmatch import fnmatchcase
import hashlib
from pathlib import Path

from secret_history import __version__
from secret_history.detectors import RULES_VERSION, classify, extract, is_env_path, selected_detectors
from secret_history.git_history.reader import GitReader
from secret_history.reporting.redaction import safe_path
from secret_history.reporting.report import FINGERPRINT_SCHEME, candidate_record, fingerprint


def _candidate_values(candidate):
    return tuple(sorted((binding.name, binding.value) for binding in candidate.bindings))


def scan_repository(repository: Path, ref: str = "HEAD", *, git: str = "git",
                    max_blob_bytes: int = 1_048_576, detectors="aws", mode="history",
                    all_refs=False, max_commits=None, exclude=()) -> dict:
    if max_blob_bytes <= 0 or (max_commits is not None and max_commits <= 0):
        raise ValueError("Limits must be positive.")
    if mode not in ("history", "snapshot", "staged") or (mode != "history" and (all_refs or max_commits)):
        raise ValueError("Unsupported scan mode combination.")
    selection = selected_detectors(detectors)
    if isinstance(exclude, str) or any(not pattern or not isinstance(pattern, str) for pattern in exclude):
        raise ValueError("Exclusions must be a sequence of nonempty glob patterns.")
    exclude = tuple(sorted(set(exclude)))
    reader = GitReader(repository, git=git)
    staged = None
    if mode == "staged":
        staged = reader.staged_entries()
        identity = "\n".join(f"{e.mode} {e.oid} {e.path}" for e in staged).encode("utf-8", "surrogatepass")
        reference = "index:" + hashlib.sha256(identity).hexdigest()
        commits = [reference]
    else:
        reference = reader.resolve(ref)
        commits = [reference] if mode == "snapshot" else reader.all_commits() if all_refs else reader.commits(reference)
    total_commits = len(commits)
    truncated = max_commits is not None and total_commits > max_commits
    if truncated:
        commits = commits[-max_commits:]
    parsed = {}
    raw_cache = {}
    occurrences = []
    skipped = {}
    parse_warnings = {}
    reference_values = set()
    reference_locations = set()
    reference_complete = reference in commits
    selected_occurrences = 0
    ignored_occurrences = 0
    blobs_read = 0
    bytes_read = 0
    sensitive_values = set()

    def in_scope(entry):
        return not any(fnmatchcase(entry.path, pattern) for pattern in exclude) and (selection != ("aws",) or is_env_path(entry.path))

    for commit in commits:
        entries = staged if staged is not None else reader.entries(commit)
        missing = sorted({entry.oid for entry in entries if in_scope(entry) and entry.mode in ("100644", "100755") and entry.oid not in raw_cache})
        for offset in range(0, len(missing), 64):
            contents = reader.read_blobs(missing[offset:offset + 64], max_blob_bytes)
            for oid, content in contents.items():
                reason = None
                text = None
                if content is None:
                    reason = "blob_size_limit"
                else:
                    blobs_read += 1
                    bytes_read += len(content)
                    if content.startswith(b"version https://git-lfs.github.com/spec/v1"):
                        reason = "lfs_pointer_not_resolved"
                    elif b"\0" in content:
                        reason = "binary_or_utf16_not_supported"
                    else:
                        try:
                            text = content.decode("utf-8-sig")
                        except UnicodeDecodeError:
                            reason = "non_utf8_not_supported"
                for env_path in (False, True):
                    found, warnings = extract(text, ".env" if env_path else "file.txt", selection) if text is not None else ([], [])
                    parsed[(oid, env_path)] = (found, warnings, reason)
                    for candidate in found:
                        for binding in candidate.bindings:
                            if binding.value:
                                sensitive_values.add(binding.value)
                                if candidate.detector == "pem":
                                    sensitive_values.update(line.strip() for line in binding.value.splitlines() if line.strip())
                raw_cache[oid] = reason
        for entry in entries:
            if any(fnmatchcase(entry.path, pattern) for pattern in exclude):
                ignored_occurrences += 1
                continue
            if entry.object_type == "commit":
                skip_reason = "submodule_not_scanned"
            elif not in_scope(entry):
                ignored_occurrences += 1
                continue
            elif entry.mode not in ("100644", "100755"):
                skip_reason = "non_regular_env_file" if selection == ("aws",) else "non_regular_file"
            else:
                selected_occurrences += 1
                candidates, warnings, skip_reason = parsed[(entry.oid, is_env_path(entry.path))]
            if skip_reason:
                identity = (entry.oid, entry.path, skip_reason)
                if identity not in skipped:
                    skipped[identity] = {"path": entry.path, "object_oid": entry.oid, "reason": skip_reason, "commits": []}
                skipped[identity]["commits"].append(commit)
                if commit == reference:
                    reference_complete = False
                continue
            for warning in warnings:
                identity = (entry.oid, entry.path, warning.line)
                if identity not in parse_warnings:
                    parse_warnings[identity] = {"path": entry.path, "blob_oid": entry.oid, "line": warning.line, "reason": warning.reason, "commits": []}
                parse_warnings[identity]["commits"].append(commit)
                if commit == reference:
                    reference_complete = False
            if commit == reference:
                reference_locations.add((entry.oid, entry.path))
            for candidate in candidates:
                row = candidate_record(candidate, classify(candidate), entry.path, commit)
                row.update({"blob_oid": entry.oid, "commits": [commit]})
                values = _candidate_values(candidate)
                occurrences.append((row, values, entry.path))
                if commit == reference:
                    reference_values.add(values)
                    reference_values.update(((binding.name, binding.value),) for binding in candidate.bindings)

    rows = []
    paths = {path for _, _, path in occurrences} | {row["path"] for row in (*skipped.values(), *parse_warnings.values())}
    masked_paths = {path: safe_path(path, sensitive_values) for path in paths}
    for row, values, path in occurrences:
        row["location_in_reference_snapshot"] = (row["blob_oid"], path) in reference_locations
        absent = False if values in reference_values else True if reference_complete else None
        row["absent_from_reference_snapshot"] = absent
        row["absent_from_reference_env"] = absent if row["detector"] == "aws" else None
        row["path"] = masked_paths[path]
        row["fingerprint"] = fingerprint(row)
        rows.append(row)
    for row in (*skipped.values(), *parse_warnings.values()):
        row["path"] = masked_paths[row["path"]]
    decisions = Counter(row["status"] for row in rows)
    coverage = {"commits_scanned": len(commits), "commits_available": total_commits, "history_truncated": truncated,
                "blob_occurrences": selected_occurrences, "unique_blobs_considered": len(raw_cache),
                "unique_blobs_read": blobs_read, "bytes_read": bytes_read,
                "out_of_scope_file_occurrences": ignored_occurrences,
                "complete_for_scope": not skipped and not parse_warnings and not truncated,
                "reference_snapshot_complete": reference_complete,
                "reference_env_complete": reference_complete,
                "skipped": list(skipped.values()), "parse_warnings": list(parse_warnings.values())}
    if selection == ("aws",):
        coverage.update(env_blob_occurrences=selected_occurrences, unique_env_blobs_considered=len(raw_cache), unique_env_blobs_read=blobs_read)
    return {
        "schema_version": "2.1", "scanner_version": __version__, "rules_version": RULES_VERSION,
        "reference_snapshot_oid": reference,
        "scope": {"mode": mode, "history": "all_local_refs" if all_refs else "ancestors_of_reference_including_merged_parents" if mode == "history" else mode,
                  "files": "UTF-8 regular Git blobs; AWS restricted to .env and .env.*", "detectors": list(selection),
                  "excluded_path_globs": [safe_path(pattern, sensitive_values) for pattern in exclude],
                  "uncommitted_files": mode == "staged", "max_blob_bytes": max_blob_bytes, "max_commits": max_commits},
        "fingerprint": {"algorithm": "SHA-256", "scheme": FINGERPRINT_SCHEME,
                        "identity": "commit_path_lines_masked_components_optional_columns", "raw_values_included": False},
        "coverage": coverage,
        "summary": {"candidate_records": len(rows), "decisions": dict(sorted(decisions.items())),
                    "alerts": sum(count for status, count in decisions.items() if status != "NON_SECRET")},
        "candidates": rows,
    }
