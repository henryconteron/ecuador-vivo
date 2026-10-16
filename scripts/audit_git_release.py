"""Read-only Git-index gate: keep local production and credentials out of a push.

Checks the exact staged blobs, not changing working files. This is a signature
scan, not a guarantee that every possible kind of secret can be detected.
"""
import json
import ast
import posixpath
from pathlib import PurePosixPath
import re
import subprocess
import sys


PRIVATE_PARTS = {"_local", "node_modules", ".venv", "__pycache__", ".hyperframes"}
MEDIA = {".mp4", ".mov", ".webm", ".mp3", ".wav", ".zip"}
SIGNATURES = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{36,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{50,}"),
    re.compile(rb"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}"),
    re.compile(rb"(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}(?![A-Za-z0-9])"),
)


def blocked_path(name):
    path = PurePosixPath(name)
    return (
        path.parts[0] == "videos"
        or bool(PRIVATE_PARTS.intersection(path.parts))
        or any(part.endswith(".egg-info") for part in path.parts)
        or path.name == ".env" or path.name.startswith(".env.")
        or path.name == "secrets.toml"
        or path.suffix.lower() in MEDIA | {".pem", ".key", ".pyc"}
    )


def git(*args):
    return subprocess.check_output(["git", *args])


def staged_blobs(names):
    # One Git process for the whole audit, rather than spawning one per asset.
    objects = {}
    for entry in git("ls-files", "--stage", "-z").decode().split("\0"):
        if entry:
            metadata, name = entry.split("\t", 1)
            objects[name] = metadata.split()[1]
    process = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for name in names:
            process.stdin.write((objects[name] + "\n").encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) != 3 or header[1] != b"blob":
                raise ValueError("The staged object is not a regular file: " + name)
            size = int(header[2])
            blob = process.stdout.read(size)
            if len(blob) != size or process.stdout.read(1) != b"\n":
                raise ValueError("Incomplete staged blob: " + name)
            yield name, blob
    finally:
        process.stdin.close()
        process.stdout.close()
        if process.wait() != 0:
            raise RuntimeError("Git blob audit failed")


def audit():
    names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").decode().split("\0")
    findings, total, count = [], 0, 0
    indexed = set(filter(None, git("ls-files", "-z").decode().split("\0")))
    for name, blob in staged_blobs(filter(None, names)):
        count += 1
        if blocked_path(name):
            findings.append({"file": name, "issue": "private_or_unpublished_path"})
        total += len(blob)
        if len(blob) >= 100 * 1024 * 1024:
            findings.append({"file": name, "issue": "github_file_size_limit"})
        if any(pattern.search(blob) for pattern in SIGNATURES):
            # Never print credentials, matching text or patch contents.
            findings.append({"file": name, "issue": "possible_credential_signature"})
        if name.endswith(".py"):
            try:
                ast.parse(blob, filename=name)
            except (SyntaxError, ValueError):
                findings.append({"file": name, "issue": "python_syntax"})
        if "/frontend/build/" in name and name.endswith(".js"):
            for target in re.findall(rb'''(?:from\s*|import\s*\(\s*)["'](\./[^"']+\.(?:js|css))["']''', blob):
                relative = posixpath.normpath(posixpath.join(posixpath.dirname(name), target.decode()))
                if relative not in indexed:
                    findings.append({"file": name, "issue": "missing_built_import", "target": relative})
    return {"staged_files": count, "staged_bytes": total, "findings": findings}


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(bool(result["findings"]))
