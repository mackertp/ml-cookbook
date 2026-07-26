# ML-Cookbook

Machine learning, a sub-set of data science and [artificial intelligence](https://www.youtube.com/watch?v=DZ9lkA6Uuvc&list=LL&index=5), is all about exploring and modeling data to classify qualitative data or estimate (predict) an outcome based on quantitative data. 

This repo shares several recipes to cook with in your "ml-kitchen". [Poetry](https://python-poetry.org/) is implemented for packaging and dependency management

Folder structure:

    .
    ├── bioinformatics          # Open-source research
    ├── networks                # Conceptual necessities 
    ├── robotics                
    ├── .gitignore
    ├── Dockerfile              # Recipe that Docker uses to create a container image
    ├── launch.sh               # Command to run an app for a deployment
    ├── poetry.lock             # Pinned dependencies (poetry)
    ├── pyproject.toml          # Project config (poetry)
    ├── ReadMe.md         
    └── requirements.txt        # Auto-generated dependency file (poetry)

**Notice on requirements.txt**: [Generate it from toml](https://testdriven.io/tips/eb1fb0f9-3547-4ca2-b2a8-1c037ba856d8/). Once requirements are installed with poetry, run jupyter-lab

```console
uname@os:~$ poetry shell
uname@os:~$ poetry install
uname@os:~$ jupyter-lab
```

### Project Jupyter 

[Jupyter is a tool](https://jupyter.org/) that will help you conduct research. This can be useful for many purposes but requires focus. All good projects start with clear goals, a scope, and some level of success criteria. There are different directions you could take... many paths to many outcomes.

**Note:** This is not an application or product, the goal is to organize technical notes. You'll need to [spark some debate](https://www.youtube.com/watch?v=ohDB5gbtaEQ) to derive value from it.
