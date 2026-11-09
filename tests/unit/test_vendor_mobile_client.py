"""Pin the mobile B2C profile of the vendored wrapper.

These tests fail if the client id, redirect URI, policy, scope or the
``offline_access`` refresh of the vendored copy drift away from the mobile
application's values, which is what makes the ~90-day sliding session possible
(see hydroqc/hydroqc#11 the change is a copy of).
"""

from __future__ import annotations

import hydroqc
from hydroqc.hydro_api.client import VENDORED_WRAPPER_VERSION, HydroClient
from hydroqc.hydro_api.consts import (
    AUTH_CALLBACK_URL,
    AUTHORIZE_URL,
    AZB2C_CLIENT_ID_MOBILE,
    AZB2C_CLIENT_ID_WEB,
    AZB2C_POLICY,
    AZB2C_SCOPE_MOBILE,
    CONSO_CSV_URL,
    INFOBASE_URL,
    RELATION_URL,
    TOKEN_URL,
)
from hydroqc.webuser import WebUser


def test_vendored_copy_imports_from_the_vendor_directory() -> None:
    """The wrapper resolves to the integration's vendored copy."""
    assert "vendor/hydroqc" in hydroqc.__file__.replace("\\", "/")


def test_the_auth_profile_is_the_mobile_client() -> None:
    """The vendored copy logs in with the Android application's client."""
    assert AZB2C_POLICY == "B2C_1A_PRD_signup_signin_mobile"
    assert AZB2C_CLIENT_ID_MOBILE == "70cd7b23-de9a-4d74-8592-d378afbfb863"
    assert AZB2C_CLIENT_ID_MOBILE != AZB2C_CLIENT_ID_WEB
    assert "offline_access" in AZB2C_SCOPE_MOBILE
    assert "hq-clientele-mobile/Espace.Client" in AZB2C_SCOPE_MOBILE
    assert AUTH_CALLBACK_URL.startswith("msauth://com.hydroquebec.mf_android/")

    # The B2C endpoints carry the mobile policy segment.
    assert "b2c_1a_prd_signup_signin_mobile/oauth2/v2.0/authorize" in AUTHORIZE_URL
    assert "b2c_1a_prd_signup_signin_mobile/oauth2/v2.0/token" in TOKEN_URL

    # The private data endpoints moved to the /wsapi/mobile/ tree.
    assert "/wsapi/mobile/prive/" in RELATION_URL
    assert "/wsapi/mobile/prive/" in INFOBASE_URL
    # The consumption CSV stays on the /lsw/portail/ bridge.
    assert "/lsw/portail/" in CONSO_CSV_URL


async def test_a_fresh_client_reports_the_vendored_identity() -> None:
    """The user agent does not need the pip package any more."""
    client = HydroClient("user@example.com", "secret", verify_ssl=True)
    assert client._cached_version is None
    await client._get_user_agent()
    assert client._cached_version == VENDORED_WRAPPER_VERSION


def test_session_state_records_the_mobile_client() -> None:
    """An exported session carries the client id it was issued for."""
    webuser = WebUser("user@example.com", "secret", verify_ssl=True)
    client = webuser._hydro_client
    client.refresh_token = "mobile-refresh-token"
    state = client.export_session_state()
    assert (
        state["client_id"] == "70cd7b23-de9a-4d74-8592-d378afbfb863"
    )


def test_import_drops_legacy_web_sessions() -> None:
    """A stored web-client session is ignored so the caller re-logs in cleanly.

    Before the mobile switch the integration stored sessions without a
    ``client_id``: they hold web tokens that cannot be refreshed by the mobile
    client.
    """
    client = HydroClient("user@example.com", "secret", verify_ssl=True)
    client.import_session_state({"refresh_token": "web-token"})
    assert client.refresh_token != "web-token"
    assert client.is_session_expired() is True

    client = HydroClient("user@example.com", "secret", verify_ssl=True)
    client.import_session_state(
        {"client_id": "09b0ae72-6db8-4ecc-a1be-041b67afc1cd", "refresh_token": "web-token"}
    )
    assert client.refresh_token != "web-token"


def test_import_accepts_mobile_sessions() -> None:
    """A session exported by the mobile client is restored."""
    client = HydroClient("user@example.com", "secret", verify_ssl=True)
    client.import_session_state(
        {
            "client_id": "70cd7b23-de9a-4d74-8592-d378afbfb863",
            "refresh_token": "mobile-refresh-token",
            "refresh_token_expiry": "2999-01-01T00:00:00",
        }
    )
    assert client.refresh_token == "mobile-refresh-token"
    assert client.is_session_expired() is False
