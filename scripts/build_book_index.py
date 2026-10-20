"""Build the Pages book list, preserving the source directory hierarchy."""

import argparse
from dataclasses import dataclass, field
from html import escape
from pathlib import Path, PurePosixPath
from urllib.parse import quote


@dataclass
class BookNode:
    children: dict[str, "BookNode"] = field(default_factory=dict)
    slug: str | None = None


PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Reading Lab</title>
  <style>
    body {
      max-width: 820px;
      margin: 48px auto;
      padding: 0 20px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.65;
    }
    h1 { margin-bottom: 8px; }
    ul { padding-inline-start: 1.4rem; }
    li { margin: 0.45rem 0; overflow-wrap: anywhere; }
    .group-label { font-weight: 600; }
    .book-list ul {
      margin: 0.35rem 0 0.75rem;
      border-inline-start: 1px solid #d4d8de;
    }
    a:focus-visible { outline: 2px solid currentColor; outline-offset: 3px; }
  </style>
</head>
<body>
  <main>
    <h1>Reading Lab</h1>
    <p>Quarto notes rendered from the repository.</p>
    <nav aria-label="书籍列表">
<!-- BOOK_LIST -->
    </nav>
  </main>
</body>
</html>
"""


def render_index(entries: list[tuple[PurePosixPath, str]]) -> str:
    root = BookNode()
    for book_path, slug in sorted(entries):
        node = root
        for part in book_path.parts:
            node = node.children.setdefault(part, BookNode())
        node.slug = slug

    def render_list(node: BookNode, depth: int = 0) -> list[str]:
        indent = "      " + "  " * depth
        list_class = ' class="book-list"' if depth == 0 else ""
        lines = [f"{indent}<ul{list_class}>"]
        for label, child in node.children.items():
            title = escape(label)
            if child.slug is not None:
                href = escape(f"./{quote(child.slug, safe='')}/", quote=True)
                title = f'<a href="{href}">{title}</a>'
            if child.children:
                lines.append(f'{indent}  <li class="book-group">')
                lines.append(f'{indent}    <span class="group-label">{title}</span>')
                lines.extend(render_list(child, depth + 2))
                lines.append(f"{indent}  </li>")
            else:
                lines.append(f"{indent}  <li>{title}</li>")
        lines.append(f"{indent}</ul>")
        return lines

    return PAGE.replace("<!-- BOOK_LIST -->", "\n".join(render_list(root)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--books-dir", type=Path, default=Path("books"))
    parser.add_argument("--output", type=Path, default=Path("public/index.html"))
    parser.add_argument(
        "--manifest",
        type=Path,
        help="NUL-separated pairs of book project paths relative to books/ and published slugs",
    )
    args = parser.parse_args()

    if args.manifest is not None:
        fields = args.manifest.read_bytes().decode("utf-8").split("\0")
        if fields[-1] == "":
            fields.pop()
        if len(fields) % 2:
            parser.error(
                "manifest must contain pairs of project paths and published slugs"
            )
        entries = [
            (PurePosixPath(project).parent, slug)
            for project, slug in zip(fields[::2], fields[1::2])
        ]
    else:
        entries = [
            (
                PurePosixPath(
                    config.parent.parent.relative_to(args.books_dir).as_posix()
                ),
                config.parent.parent.name,
            )
            for config in args.books_dir.glob("**/book/_quarto.yml")
        ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_index(entries), encoding="utf-8")


if __name__ == "__main__":
    main()
