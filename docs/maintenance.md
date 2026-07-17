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

## Python 与 Julia 混写

需要在同一个 QMD 文件中混写 Julia 和 Python 时，以 Julia 作为文档引擎，并通过 PythonCall 执行 Python：

```yaml
---
engine: julia
julia:
  env:
    - "JULIA_PYTHONCALL_EXE=@venv"
    - "JULIA_CONDAPKG_BACKEND=Null"
    - "PYTHONPATH=../../../.."
    - "NO_COLOR=1"
---
```

文件开头先加载 PythonCall：

````markdown
```{julia}
import PythonCall
```
````

之后即可同时使用 `{julia}` 和 `{python}` 代码块。Python 依赖由根目录的 `pyproject.toml` 和 `uv.lock` 管理，Julia 依赖由 `Project.toml` 和 `Manifest.toml` 管理。更新依赖后应同时提交对应的清单和锁文件。

本地首次渲染前运行：

```powershell
uv sync --locked
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

CI 会在临时渲染目录中复制 Julia 项目文件，并把根目录的 `.venv` 链接过去。因此 QMD 中应使用 `JULIA_PYTHONCALL_EXE=@venv`，不要写死本机 Python 路径。

### Python 富输出

Julia 引擎中的 Python 代码由 PythonCall 执行，不存在 IPython/Jupyter 的 display publisher。仓库提供了共享适配器 `books/assets/reading_lab_display.py`：在 Zed/IPython 中，它调用 IPython 原生富显示；在 Quarto/PythonCall 中，它把 Markdown、HTML 和 SymPy LaTeX 输出给 Pandoc。

对于位于 `books/<书名>/book/chapters/` 的混编 QMD，先在上面的 `julia.env` 中设置 `PYTHONPATH=../../../..`，然后在第一个 Python 代码块中导入共享 `display`：

````markdown
```{python}
#| output: asis

import sympy as sp
from IPython.display import Markdown
from books.assets.reading_lab_display import display

A = sp.Matrix([[1, 0, -2], [0, 1, sp.Rational(3, 2)]])
display(Markdown("行最简矩阵："), A)
```
````

同一 QMD 完整渲染时，各个 Python 代码块共享命名空间，后续代码块可以继续使用 `display`。如果希望在 Zed 中单独执行某个代码块，则在该块中重复导入。

可以从 `IPython.display` 导入 `Markdown`、`Math` 等对象，但不要导入它的 `display`：

```python
# 正确
from IPython.display import Markdown
from books.assets.reading_lab_display import display

# 错误：会覆盖共享适配器
from IPython.display import Markdown, display
```

每个需要显示 Markdown、HTML 或 LaTeX 的 Python 代码块都要设置 `#| output: asis`。它会把打印结果重新交给 Pandoc 解析；共享适配器会自动用空行分隔多个对象。普通的纯文本计算块不需要这个选项。

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
