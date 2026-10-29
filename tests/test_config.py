import pytest

from app import create_app


@pytest.mark.parametrize("secret_key", [None, "", "short"])
def test_production_rejects_weak_secret_key(secret_key):
    class ProductionConfig:
        DEBUG = False
        TESTING = False
        SECRET_KEY = secret_key

    with pytest.raises(RuntimeError, match="Production requires a SECRET_KEY"):
        create_app(ProductionConfig)
