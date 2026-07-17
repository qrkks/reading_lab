"""Display rich Python objects in both IPython and Quarto's Julia engine."""

from typing import Any


def _active_ipython_display():
    try:
        from IPython import get_ipython
        from IPython.display import display as ipython_display
    except ImportError:
        return None

    shell = get_ipython()
    if shell is None or getattr(shell, "display_pub", None) is None:
        return None
    return ipython_display


def _emit_asis(obj: Any) -> None:
    if isinstance(obj, (list, tuple)):
        for item in obj:
            _emit_asis(item)
        return

    for method_name in ("_repr_markdown_", "_repr_latex_", "_repr_html_"):
        method = getattr(obj, method_name, None)
        if method is None:
            continue
        rendered = method()
        if rendered is not None:
            print(rendered)
            print()
            return

    print(obj)
    print()


def display(*objects: Any) -> None:
    """Use IPython rich display when available, otherwise emit Quarto as-is output."""
    ipython_display = _active_ipython_display()
    if ipython_display is not None:
        ipython_display(*objects)
        return

    for obj in objects:
        _emit_asis(obj)
