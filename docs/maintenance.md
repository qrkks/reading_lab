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

### Python 富输出和换行

Julia 引擎中的 Python 代码由 PythonCall 执行，不存在 IPython/Jupyter 的 display publisher。直接调用 `IPython.display()` 时，SymPy 对象可能退化为普通文本。需要输出 Markdown 或 SymPy LaTeX 时，采用下面的兼容写法：

````markdown
```{python}
#| output: asis
from IPython.display import Markdown


def display(*objects):
    # Render IPython-style objects when Python runs inside Julia/PythonCall.
    for obj in objects:
        if isinstance(obj, Markdown):
            print(obj.data)
        elif hasattr(obj, "_repr_latex_") and obj._repr_latex_():
            print(obj._repr_latex_())
        elif isinstance(obj, (list, tuple)):
            display(*obj)
            continue
        else:
            print(obj)
        print()
```
````

`output: asis` 会把输出重新交给 Pandoc 作为 Markdown 解析。Markdown 中普通的单换行会被折叠为空格，所以兼容函数必须在每个对象后额外执行一次 `print()`，用空行分隔输出段落。

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
