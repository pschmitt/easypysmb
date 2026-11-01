# Agent instructions

`easypysmb` is a Python wrapper library for PySMB. Keep its public API and SMB behavior consistent with the existing implementation and tests.

## Working and validation

- Use the repository's Poetry configuration for dependencies and development checks.
- Run focused tests and the configured Flake8 and Black checks for changes; use fixtures or mocks rather than a live SMB service.
- Before changing GitHub Actions, check whether [pschmitt/ci-workflows](https://github.com/pschmitt/ci-workflows) provides a reusable workflow or action. Preserve current behavior and check coverage, and use `@main` for shared workflow or action references.
