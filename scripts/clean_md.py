"""Strip PDF-footer noise (disclaimers, page numbers, repeated bylines) from extracted markdown."""
import pathlib
import re
import sys

DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs"

# Lines to drop entirely (case-insensitive substring match against stripped line)
NOISE_SUBSTRINGS = [
    "made by skipper",
    "disclaimer - not financial advice",
    "trading is your own responsibility",
    "this is not financial advise",  # alt spelling used in the guidebook
]

# Whole-line patterns to drop (after stripping markdown emphasis/whitespace)
NOISE_REGEXES = [
    re.compile(r"^\s*\d+\s*$"),                                           # bare page numbers
    re.compile(r"^\s*page\s+\d+(\s+of\s+\d+)?\s*$", re.IGNORECASE),       # "Page N" / "Page N of M"
]


def strip_emphasis(s: str) -> str:
    return re.sub(r"[*_`]", "", s).strip()


def is_noise(line: str) -> bool:
    bare = strip_emphasis(line).lower()
    if not bare:
        return False
    if any(s in bare for s in NOISE_SUBSTRINGS):
        return True
    if any(rx.match(line) for rx in NOISE_REGEXES):
        return True
    return False


def clean(path: pathlib.Path) -> int:
    text = path.read_text()
    out, dropped = [], 0
    for line in text.splitlines():
        if is_noise(line):
            dropped += 1
            continue
        out.append(line)

    cleaned = "\n".join(out)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    if not cleaned.endswith("\n"):
        cleaned += "\n"

    if dropped:
        path.write_text(cleaned)
    return dropped


if __name__ == "__main__":
    targets = [DOCS / a for a in sys.argv[1:]] if len(sys.argv) > 1 else sorted(DOCS.glob("*.md"))
    total = 0
    for p in targets:
        n = clean(p)
        if n:
            print(f"  {p.name}: dropped {n} noise lines")
            total += n
    print(f"total dropped: {total}")
