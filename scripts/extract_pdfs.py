"""Convert PDFs to markdown with per-doc image folders following the docs/ convention."""
import pathlib
import re
import sys
import pymupdf4llm

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
IMG_ROOT = DOCS / "images"


def extract(pdf_path: pathlib.Path, slug: str) -> None:
    img_dir = IMG_ROOT / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    md = pymupdf4llm.to_markdown(
        str(pdf_path),
        write_images=True,
        image_path=str(img_dir),
        image_format="png",
        dpi=200,
    )

    # pymupdf4llm emits paths relative to CWD (e.g. "docs/images/<slug>/...")
    # we want them relative to the .md file's location (docs/), so strip "docs/"
    md = md.replace(f"docs/images/{slug}/", f"images/{slug}/")
    md = md.replace(f"{img_dir}/", f"images/{slug}/")  # absolute-path fallback
    md = md.replace(f"images/{slug}/{pdf_path.name}-", f"images/{slug}/")

    # clean redundant prefix on disk too: <pdf-stem>.pdf-0002-08.png -> 0002-08.png
    prefix = f"{pdf_path.name}-"
    for p in img_dir.glob(f"{prefix}*"):
        p.rename(img_dir / p.name[len(prefix):])

    out = DOCS / f"{slug}.md"
    out.write_text(md)
    n_imgs = len(list(img_dir.iterdir()))
    print(f"  {pdf_path.name} -> {out.name}  ({n_imgs} images)")


# Slugs are derived from the in-document title, not the source filename.
# Add (input-pdf-relative-path, output-slug) pairs as needed.
JOBS: list[tuple[str, str]] = []

if __name__ == "__main__":
    force = "--force" in sys.argv
    for rel, slug in JOBS:
        pdf = ROOT / rel
        if not pdf.exists():
            print(f"MISSING {pdf}", file=sys.stderr)
            continue
        if not force and (DOCS / f"{slug}.md").exists():
            print(f"  skip {slug} (already extracted; --force to redo)")
            continue
        extract(pdf, slug)
