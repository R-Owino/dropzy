import pytest


@pytest.fixture(autouse=True)
def ignore_session_warnings():
    import warnings
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module="flask_session.*"
    )
