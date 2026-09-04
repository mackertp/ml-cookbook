# ML-Cookbook

Machine learning, a subset of data science and [artificial intelligence](https://www.youtube.com/watch?v=DZ9lkA6Uuvc&list=LL&index=5), is all about exploring and modeling data to classify qualitative data or estimate (predict) an outcome based on quantitative data. 

This repo shares several recipes to cook with in your "ml-kitchen." [Poetry](https://python-poetry.org/) is implemented for packaging and dependency management.

Folder structure:

```
.
├── algorithms              # ¯\_(ツ)_/¯
├── bioinformatics          # Open-source research
├── networks                # [Conceptual necessities](https://youtube.com/shorts/6xQBg5LEI5I?si=_3KdKi3GBTC9domo) 
├── robotics
├── .gitignore
├── poetry.lock             # Pinned dependencies (poetry)
├── pyproject.toml          # Project config (poetry)
├── ReadMe.md               
└── requirements.txt        # Auto-generated dependency file (poetry)
```

**Notice on requirements.txt**: [Generate it from TOML](https://testdriven.io/tips/eb1fb0f9-3547-4ca2-b2a8-1c037ba856d8/). Once requirements are installed with poetry, run jupyter-lab. I suggest you decouple the projects by running jupyter-lab from a specific directory.

```console
uname@os:~$ poetry env activate
uname@os:~$ poetry install
uname@os:~$ cd ../folder_selected/
uname@os:~$ jupyter-lab
```

### Project Jupyter

[Jupyter is a tool](https://jupyter.org/) that will help you conduct research and document ideas.
