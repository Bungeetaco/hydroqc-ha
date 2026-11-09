# Vendored copy of the Hydro-Québec API wrapper

This directory holds a vendored copy of
[hydroqc/hydroqc](https://github.com/hydroqc/hydroqc) (`Hydro-Quebec-API-Wrapper`,
official releases 4.3.1) so that this integration can ship its own authentication
profile without depending on a released wrapper version.

## Why it is vendored

Upstream released versions log in with the **web** Azure AD B2C client. Since
Hydro-Québec added an e-mail verification step to that policy, its refresh token
is capped at about 24 h: the integration has to re-authenticate (and e-mail a
new verification code) every day.

Copied here is upstream `main` (identical to release 4.3.1) plus the change
proposed in [hydroqc#11](https://github.com/hydroqc/hydroqc/pull/11):

* Azure AD B2C **mobile client** (`b2c_1a_prd_signup_signin_mobile` policy,
  client id `70cd7b23-de9a-4d74-8592-d378afbfb863`, `msauth://` redirect, the
  `hq-clientele-mobile/Espace.Client` audience and the `offline_access` scope).
* Private data calls moved from `/wsapi/web/prive/` to `/wsapi/mobile/prive/`
  (the mobile audience token is refused by the web endpoints).
* `export_session_state()` records `client_id`; `import_session_state()` drops a
  state issued for another client, so an upgrade falls back to a clean
  interactive login instead of a silent refresh failure.
* This copy also short-circuits the wrapper's pip-metadata lookup (the version
  is taken from upstream release 4.3.1), as the wrapper is not installed as a
  pip package any more.

Validated live on 2026-11-08 against a real account: login (one e-mail
verification code), `/wsapi/mobile` relations / contract summary / infoCompte /
contracts, `maj-session` portal bridge, monthly/daily/hourly consumption,
history CSV, and a refresh exchange showing a ~90-day sliding refresh token.

## How it is imported

`custom_components/hydroqc/__init__.py` prepends this `vendor` directory to
`sys.path` before importing `hydroqc`, which resolves to the copy here. The
copy keeps its own `hydroqc.*` internal imports to stay in sync with upstream
(vendoring a future release is then a pure file copy plus the profile diff).

## License

The wrapper is LGPL-3.0-or-later. The `LICENSE` file here is its upstream
license; this vendoring preserves the copyright of the Hydroqc team.
