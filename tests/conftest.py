import os
from unittest import mock

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_terminal_columns():
    with mock.patch.dict(os.environ, {"COLUMNS": "100"}):
        yield
