import time

import pytest
from azure.core.credentials import AccessToken
from azure.identity import AzureCliCredential, ClientSecretCredential

from models.azure_auth import REFRESH_MARGIN_SECONDS, CachedToken, get_azure_credential


@pytest.fixture
def service_principal_env(monkeypatch):
    monkeypatch.delenv("AZURE_SQL_AUTH", raising=False)
    monkeypatch.setenv("TENANT_ID", "tenant")
    monkeypatch.setenv("FABRIC_CLIENT_ID", "client")
    monkeypatch.setenv("FABRIC_SECRET", "secret")


class FakeCredential:
    def __init__(self, lifetime: int):
        self.lifetime = lifetime
        self.calls = 0

    def get_token(self, *scopes, **kwargs):
        self.calls += 1
        return AccessToken(f"token-{self.calls}", int(time.time()) + self.lifetime)


def test_service_principal_is_the_default(service_principal_env):
    assert isinstance(get_azure_credential(), ClientSecretCredential)


def test_cli_mode_needs_no_secret(monkeypatch):
    monkeypatch.setenv("AZURE_SQL_AUTH", "cli")
    monkeypatch.delenv("FABRIC_SECRET", raising=False)
    assert isinstance(get_azure_credential(), AzureCliCredential)


def test_unknown_mode_is_refused(service_principal_env, monkeypatch):
    monkeypatch.setenv("AZURE_SQL_AUTH", "password")
    with pytest.raises(ValueError, match="AZURE_SQL_AUTH"):
        get_azure_credential()


def test_missing_secret_explains_the_cli_alternative(service_principal_env, monkeypatch):
    monkeypatch.delenv("FABRIC_SECRET")
    with pytest.raises(ValueError, match="az login"):
        get_azure_credential()


def test_token_is_reused_while_valid():
    credential = FakeCredential(lifetime=3600)
    cached = CachedToken(credential, "scope")
    assert cached.get() == cached.get() == "token-1"
    assert credential.calls == 1


def test_token_is_refreshed_near_expiry():
    credential = FakeCredential(lifetime=REFRESH_MARGIN_SECONDS - 1)
    cached = CachedToken(credential, "scope")
    assert cached.get() == "token-1"
    assert cached.get() == "token-2"
