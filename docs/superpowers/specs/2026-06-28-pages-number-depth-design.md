# Pages Number Depth Design

## Goal

Allow each Quarto book to choose its own section-numbering depth for GitHub
Pages while retaining the repository-wide HTML default.

## Source of truth

- A book-specific value is declared as top-level `number-depth` in the book's
  `_quarto.yml`.
- If that key is absent, Pages uses `format.html.number-depth` from the root
  `_quarto-html.yml`, currently `3`.
- Format-specific values remain valid only when HTML and DOCX intentionally
  need different numbering depths.

## Publishing flow

For each book, the Pages workflow will:

1. Copy the root `_quarto-html.yml` to a temporary metadata template.
2. Read only an unindented, top-level `number-depth` from the book's
   `_quarto.yml`.
3. When a book value exists, replace the HTML template's `number-depth` with
   that value; otherwise leave the default unchanged.
4. Copy the resulting metadata into the temporary document directories and
   render the HTML book as before.

This preserves the existing `_metadata.yml` publishing mechanism and avoids
adding a YAML-processing dependency for one scalar option.

## Existing books

Existing intentional `number-depth` values nested under `format.docx` will be
moved to the top level so local DOCX and remote HTML share the same value. The
already-top-level MIT 18.06 value remains unchanged. Other books continue to
inherit the Pages default of `3`.

## Verification

- Simulate metadata generation for MIT 18.06 and confirm Pages receives `2`.
- Simulate a book without top-level `number-depth` and confirm Pages receives
  the root default `3`.
- Validate all edited YAML and ensure the workflow still discovers and renders
  every book through its existing loop.

## Scope

The change affects only numbering-depth selection. Themes, TOCs, DOCX-only
options, book discovery, output paths, and deployment behavior remain
unchanged.
