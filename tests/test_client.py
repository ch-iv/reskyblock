import pytest
from reskyblock import Client


def test_client():
    with pytest.raises(NotImplementedError):
        _ = Client()
