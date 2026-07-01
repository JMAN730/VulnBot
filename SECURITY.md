# Security Policy

## Public Alpha Status

VulnBot is public alpha software for authorized security testing, CTFs, labs, and
controlled research. Do not treat it as a production security control, a strong
sandbox, or an authorization mechanism.

Some capabilities intentionally perform security testing actions. Use them only
against systems where you have explicit permission and a written scope.

## Supported Versions

Security fixes are applied to the current `main` branch and the latest published
release line. Older alpha releases may not receive backports.

## Reporting Vulnerabilities

Please do not open a public issue for exploitable vulnerabilities, credential
exposure, sandbox escapes, or issues that could enable abuse.

Report privately through GitHub's private vulnerability reporting feature if it
is enabled for the repository. If that is unavailable, contact the maintainers
listed in `pyproject.toml` and include:

- Affected version or commit
- Minimal reproduction steps
- Impact and affected component
- Whether any credentials, private data, or third-party systems were involved

We aim to acknowledge valid reports within 7 days. Public disclosure should wait
until a fix or mitigation is available.

## Authorized Use

VulnBot is intended solely for lawful, authorized security work. Before use,
confirm:

- The target owner explicitly authorized the test
- Scope, timing, and allowed actions are written down
- Testing will not exceed the authorized hosts, ports, paths, accounts, or data
- Local laws, platform rules, and engagement rules permit the activity

Unauthorized use may be illegal and harmful. The maintainers are not responsible
for misuse.

## Sensitive Data

Do not commit API keys, session files, reports containing third-party secrets, or
target-state data from real engagements. By default VulnBot stores local
configuration under `~/.vulnbot/`; review those files before sharing logs or
bug reports.
