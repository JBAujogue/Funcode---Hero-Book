# Hero-Book


This tiny project is a solver for Hero Books that are written in french (les _livres dont vous êtes le héros_).
The approach consists in parsing a pdf file into a structured set of episodes, and in turn represent it as a Directed Graph.
Solving the book then only amounts to finding the shortest path between the beginning and end episodes of the book.

## How to use it

### 1. Installation

Create a conda environment named _herobook_: run in a conda shell 

- `conda create -n herobook`

- `conda activate herobook`

Install python and dependencies

- `conda install pip python=3.8`

- `cd path/to/Hero-Book`

- `pip install -r requirements.txt`



### 2. Usage

Launch the jupyter notebook in order to inspect the analysis performed

- `jupyter notebook`

Or launch the Streamlit browsing interface:

- `streamlit run app.py`

You can play with both using some pdfs found in `data/pdfs`.

Enjoy !
