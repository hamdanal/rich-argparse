# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>

# for internal use only
from __future__ import annotations

from rich_argparse._argparse import RichHelpFormatter


def patch_default_formatter_class(
    cls=None, /, *, formatter_class=RichHelpFormatter, method_name="__init__"
):
    """Patch the default `formatter_class` parameter of an argument parser constructor.

    Parameters
    ----------
    cls : (type, optional)
        The class to patch. If not provided, a decorator is returned.
    formatter_class : (type, optional)
        The new formatter class to use. Defaults to ``RichHelpFormatter``.
    method_name : (str, optional)
        The method name to patch. Defaults to ``__init__``.

    Examples
    --------
    Can be used as a normal function to patch an existing class::

        # Patch the default formatter class of `argparse.ArgumentParser`
        patch_default_formatter_class(argparse.ArgumentParser)

        # Patch the default formatter class of django commands
        from django.core.management.base import BaseCommand, DjangoHelpFormatter
        class DjangoRichHelpFormatter(DjangoHelpFormatter, RichHelpFormatter): ...
        patch_default_formatter_class(
            BaseCommand, formatter_class=DjangoRichHelpFormatter, method_name="create_parser"
        )
    Or as a decorator to patch a new class::

        @patch_default_formatter_class
        class MyArgumentParser(argparse.ArgumentParser):
            pass

        @patch_default_formatter_class(formatter_class=RawDescriptionRichHelpFormatter)
        class MyOtherArgumentParser(argparse.ArgumentParser):
            pass
    """
    import functools

    def decorator(cls, /):
        method = getattr(cls, method_name)
        if not callable(method):
            raise TypeError(f"'{cls.__name__}.{method_name}' is not callable")

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            kwargs.setdefault("formatter_class", formatter_class)
            return method(*args, **kwargs)

        setattr(cls, method_name, wrapper)
        return cls

    if cls is None:
        return decorator
    return decorator(cls)
