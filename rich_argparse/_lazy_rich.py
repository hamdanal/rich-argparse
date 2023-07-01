# for private use only
from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = [
    "Console",
    "ConsoleOptions",
    "RenderableType",
    "RenderResult",
    "Lines",
    "escape",
    "StyleType",
    "Span",
    "Text",
    "Theme",
]

if TYPE_CHECKING:
    from rich.console import Console as Console
    from rich.console import ConsoleOptions as ConsoleOptions
    from rich.console import RenderableType as RenderableType
    from rich.console import RenderResult as RenderResult
    from rich.containers import Lines as Lines
    from rich.markup import escape as escape
    from rich.style import StyleType as StyleType
    from rich.text import Span as Span
    from rich.text import Text as Text
    from rich.theme import Theme as Theme


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)  # pragma: no cover
    import rich.console
    import rich.containers
    import rich.markup
    import rich.style
    import rich.text
    import rich.theme

    exported = {
        "Console": rich.console.Console,
        "ConsoleOptions": rich.console.ConsoleOptions,
        "RenderableType": rich.console.RenderableType,
        "RenderResult": rich.console.RenderResult,
        "Lines": rich.containers.Lines,
        "escape": rich.markup.escape,
        "StyleType": rich.style.StyleType,
        "Span": rich.text.Span,
        "Text": rich.text.Text,
        "Theme": rich.theme.Theme,
    }
    return exported[name]
