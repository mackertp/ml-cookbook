# ML-Cookbook

Machine learning, a sub-set of data science and artificial intelligence, is all about exploring and modeling data to classify qualitative data or estimate (predict) an outcome based on quantitative data. This repo shares a number of recipies to cook with in your "ml-kitchen". 

[Poetry](https://python-poetry.org/) is implemented for packaging and dependency management, the folder structure shared below

    .
    ├── bioinformatics          # Open source research
    ├── languages               # Pick your poison
    ├── networks                # Conceptual necessities 
    ├── robotics                
    ├── .gitignore
    ├── Dockerfile              # Recipe that Docker uses to create a container image
    ├── launch.sh               # Command to run an app for a deployment
    ├── poetry.lock             # Pinned dependencies (poetry)
    ├── pyproject.toml          # Project config (poetry)
    ├── ReadMe.md         
    └── requirements.txt

**Notice on requirements.txt**: [Generate it from toml](https://testdriven.io/tips/eb1fb0f9-3547-4ca2-b2a8-1c037ba856d8/). Once requirements are installed with poetry, run jupyter-lab

```console
uname@os:~$ poetry shell
uname@os:~$ poetry install
uname@os:~$ jupyter-lab
```

## Project Jupyter 

Jupyter is a tool that will help you conduct research. This can be useful for a lot of purposes, but requires detail and some focus. All good projects start with clear goals, a scope, and some level of success criteria. There are a lot of different directions you could take... many paths to many outcomes. Remember, this is just a tool - [official site](https://jupyter.org/).

**Note:** This is not an application or product, the goal here is to organize technical notes. You'll need to [spark some debate](https://www.youtube.com/watch?v=ohDB5gbtaEQ) to derive value from it.

#### **Further Research**
Ask me about [sip-research](https://sip-research.com).