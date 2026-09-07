# Update and Publish to PyPI

Run the following steps from this folder to update and publish `prm-studio`. The `yarn` package manager is preferred for frontend assets.

### 1. Bump package version

Edit `setup.cfg` and increase `version` (e.g.: `0.1.1` -> `0.1.2`).

### 2. Rebuild CSS assets

```console
yarn install
yarn build
```

### 3. Build fresh Python artifacts

```console
rm -rf dist build src/prm_studio.egg-info
poetry run python -m build
poetry run python -m twine check dist/*
```

### 4. Upload to PyPI with API token (non-interactive)

Ensure the pypi token is stored in `.env` as `pypi_token='pypi-...'`, use:

```console
TOKEN=$(sed -n "s/^pypi_token='\(.*\)'$/\1/p" /Users/prestonmackert/Documents/code/ml-cookbook/.env)
TWINE_USERNAME=__token__ TWINE_PASSWORD="$TOKEN" \
poetry run python -m twine upload --non-interactive --verbose dist/*
```

### 5. Verify release

```console
poetry run python -m pip index versions prm-studio | head
```

or open:

[https://pypi.org/project/prm-studio/](https://pypi.org/project/prm-studio/)


### 6. Upgrade consuming Poetry project

From the root:

```bash
poetry add prm-studio@latest
poetry show prm-studio
```

### Common errors

- `400 File already exists`: you must bump the version and rebuild.
- `NonInteractive: Credential not found for API token`: set `TWINE_USERNAME` and `TWINE_PASSWORD` as shown above.