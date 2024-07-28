from tests.dummy_repo.src.functions import add


def test_add():
    assert add(2, 4) == 6
