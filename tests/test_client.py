import pytest

from reskyblock import Client


@pytest.fixture
def client() -> Client:
    return Client()


def test_client() -> None:
    _ = Client()


def test_get_auctions(client: Client) -> None:
    client.get_auctions()


def test_get_auctions_ended(client: Client) -> None:
    client.get_auctions_ended()
