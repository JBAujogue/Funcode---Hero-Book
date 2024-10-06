# Hero-Book
This tiny project is a solver for Hero Books that are written in french (les _livres dont vous êtes le héros_).<br>
The approach consists in parsing a pdf file into a structured set of episodes, and representing this set as a Directed Graph. Solving the book then only amounts to finding the shortest path between the beginning and end episode of the book.


## How to use it
### 1. Installation
This project uses python `3.11` as core interpreter, conda as environment manager, and poetry `1.8` as dependency manager.<br>
Create a new conda environment
```shell
conda env create -f environment.yml
```
Activate the environment
```shell
conda activate herobook
```
Move to the project directory and install the project dependencies
```shell
poetry install
```


### 2. Usage
Run the streamlit app:
```shell
streamlit run app.py
```
You can play with both using some pdfs found in `data/pdfs`.
Enjoy !
