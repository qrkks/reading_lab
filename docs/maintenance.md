# 维护说明

## 新增一本书

每本书保持独立的 Quarto book project，目录结构约定为：

```text
books/
  书名/
    book/
      _quarto.yml
      index.qmd
      chapters/
        1.md
```

新增后本地先渲染确认：

```powershell
quarto render "books/书名/book" --to html
```

推送到 `main` 后，`.github/workflows/quarto-pages.yml` 会自动扫描 `books/*/book/_quarto.yml`，渲染 HTML，并把书加入 Pages 首页列表；README 不需要手动维护书单。

## HTML 默认参数

GitHub Pages 使用的 HTML 共享参数在 `_quarto-html.yml`，例如主题、目录、章节编号深度、代码复制按钮等。

workflow 发布网页时不会改动原书目录，而是先把每本书复制到临时目录，再把 `_quarto-html.yml` 临时复制成各级文档目录里的 `_metadata.yml`。这样 `book/index.qmd` 和 `book/chapters/*.md` 都能吃到同一套 HTML 参数。

本地直接在某本书目录运行 `quarto render ... --to docx` 时，不会自动读取 `_quarto-html.yml`，所以不会因为 Pages 的 HTML 配置影响 docx。

## Pages 路径和 slug

Pages 发布路径由 `.github/workflows/quarto-pages.yml` 里的 `book_slug` 决定。当前配置是：

```bash
book_slug="$book_title"
```

也就是直接使用书籍目录名作为 URL 路径，例如：

```text
https://qrkks.github.io/reading_lab/统计推断（Casella）/
```

如果以后想恢复英文 slug，可以在同一个 workflow 里改回：

```bash
book_slug="$(slug_for "$book_title")"
```

然后在上方的 `slug_for()` 函数里给书名配置英文路径。没有配置映射的书，会默认使用原书名。
