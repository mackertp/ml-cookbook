# prm-studio

A shared design system package that can be implemented in Python applications, [ml-cookbook](https://github.com/mackertp/ml-cookbook) provides Flask implementations of the design system.

## What this package includes

- A compiled CSS asset at `/prm-studio/static/css/prm-studio.css`
- Reusable Jinja templates and macros under `prm_studio/`
- A Flask blueprint registration helper for static and template loading

## Install

Install prm-studio to an isolated environment with [poetry](https://python-poetry.org/).

```bash
poetry add prm-studio
```

Or with pip

```bash
pip install prm-studio
```

## Use in a Flask app

```python
from flask import Flask
from prm_studio import register_prm_studio

app = Flask(__name__)
register_prm_studio(app)
```

Then include the stylesheet in your app templates:

```jinja2
<link rel="stylesheet" href="{{ url_for('prm_studio.static', filename='css/prm-studio.css') }}">
```