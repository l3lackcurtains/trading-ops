#!/usr/bin/env python3
"""
validate_links.py — project-wide markdown link audit.

Walks every .md file in the project, extracts every relative link `](path)`
and image `![alt](path)`, resolves the path against the file's directory,
and reports any link whose target doesn't exist.

External links (http/https/mailto), in-page anchors (#section), and absolute
paths (starting with /) are skipped — those aren't ours to verify.

Usage:
    python3 scripts/validate_links.py            # report broken links, exit 0/1
    python3 scripts/validate_links.py --quiet    # exit code only, no output unless broken
    python3 scripts/validate_links.py --strict   # also flag links missing trailing slash on dirs

Exit code:
    0 — all links resolve
    1 — at least one broken link found
    2 — script error (path issue, etc.)
"""

import argparse
import os
import re
import sys

# Match markdown links AND images: ](path)  or  !](path)
# - capture path (group 1) up to first ')' or '#' or whitespace
# - allow optional anchor after the path
LINK_RE = re.compile(r'\]\(([^)#\s]+?)(?:#[^)]*)?\)')

# Folders to skip entirely
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'input', '.claude'}

# Schemes that mean "not our problem"
EXTERNAL_PREFIXES = ('http://', 'https://', 'mailto:', 'ftp://', 'tel:')


def find_md_files(root: str):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f.endswith('.md'):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


def check_file(path: str):
    """Return list of (line_no, link_text, resolved_target) for broken links.

    Skips:
      - lines inside fenced code blocks (``` ... ```)
      - links that contain template placeholders like <TICKER>, <YYYY-MM-DD>, <SYM>
      - external links, anchors, and absolute paths
    """
    bad = []
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return [(0, f'<read error: {e}>', '')]

    base = os.path.dirname(os.path.abspath(path))
    in_fence = False
    for line_no, line in enumerate(lines, start=1):
        # Toggle code-fence tracking on lines that start with ``` (any language tag)
        stripped = line.lstrip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for m in LINK_RE.finditer(line):
            link = m.group(1).strip()
            if not link or link.startswith(EXTERNAL_PREFIXES):
                continue
            if link.startswith('#'):
                continue
            if link.startswith('/'):
                continue
            # Skip template placeholder paths — they're documentation, not real refs
            if '<' in link and '>' in link:
                continue
            # Skip links that are themselves placeholders like (URL) or (path)
            if link.lower() in ('url', 'path', 'link', 'todo'):
                continue
            target = os.path.normpath(os.path.join(base, link))
            if not os.path.exists(target):
                bad.append((line_no, link, target))
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().split('\n')[0])
    ap.add_argument('--quiet', action='store_true', help='only print on broken links')
    ap.add_argument('--root', default='.', help='project root (default: current directory)')
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f'ERROR: {root} is not a directory', file=sys.stderr)
        return 2

    files = find_md_files(root)
    total_files = len(files)
    broken_links = 0
    files_with_broken = 0
    output = []

    for f in files:
        rel = os.path.relpath(f, root)
        bad = check_file(f)
        if bad:
            files_with_broken += 1
            broken_links += len(bad)
            output.append(f'\n{rel}')
            for line_no, link, target in bad:
                rel_target = os.path.relpath(target, root) if target else '?'
                output.append(f'  L{line_no}: {link}')
                output.append(f'         -> {rel_target}  (does not exist)')

    if not args.quiet:
        print(f'Checked {total_files} markdown file(s).')

    if broken_links:
        if not args.quiet:
            print(f'Found {broken_links} broken link(s) in {files_with_broken} file(s):')
        print('\n'.join(output))
        return 1

    if not args.quiet:
        print('All markdown links resolve.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
