# ml-cookbook

This repository serves as a reference for machine learning research. I own Aurélien Géron's [Hands-On Machine Learning with Scikit-Learn & Tensorflow](https://www.google.com/books/edition/Hands_On_Machine_Learning_with_Scikit_Le/bRpYDgAAQBAJ?hl=en&gbpv=1&printsec=frontcover) and am storing my version of the code for that book in the top level 'book' directory. I have ignored the book code on this repository and highly recommend that you purchase the original.

If you can't get the book and want to get started for free, start with this [Markdown reference](https://www.markdownguide.org/) to create ReadMe files like this one. 

I've also created a *languages* directory that contains configurations for the most popular and commonly used computer languages wihtin industry. My favorite language is Python and I use [Poetry](https://python-poetry.org/) to manage my projects. This repository will start off with Python, [however...](https://i1.sndcdn.com/artworks-000127323954-psfxss-t500x500.jpg)

Get started by creating a virtual Python environment, installing the project dependencies, then creating a *Jupyter Kernel*:

```console
uname@os:~$ poetry shell
uname@os:~$ poetry install
uname@os:~$ poetry run python -m ipykernel install --user --name ml-cookbook
```

Now launch the virtual lab and select the kernel so that you can execute the code Notebooks locally.

```console
uname@os:~$ jupyter-lab
```