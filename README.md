# lingdiggers
Project for the Building NLP Applications course

We have created a search engine that searches through a (small) song lyrics database and presents all occurrences of a query along with the artist and song name. 
Results are shortened to show only the query in context (and not the whole song).
Our engine supports single word and multi-word queries. 
With single word queries it looks for an occurrence anywhere within a word; e.g. if a query is 'way', our engine searches for words such as 'way', 'ways', 'away' etc. 
With multi-word queries the engine searches only for the specific words in the query; e.g. 'fix you' shows results with 'fix' and 'you'.
As we are using the tf-idf method, the results in both cases are ranked and presented in descending order.

The web UI features Bootstrap and Jinja2 to ensure that the search interface looks nice to the user. When no search query exists, the user sees a 
welcome message, and when no matches for the query are found, the user sees a special message.

To use the search engine, 3 files are needed:
- flaskdemo.py should be located in the flask folder
- lyrics2.txt is the (small) lyrics database and should be located where the python file is.
  (! the path in flaskdemo.py should be changed accordingly + depending on the operating system the encoding might need to be specified as utf-8)
- index.html located in the templates folder.

The following libraries and functions are required for the flaskdemo.py file:
- from flask import Flask, render_template, request
- from sklearn.feature_extraction.text import TfidfVectorizer
- from sklearn.feature_extraction.text import CountVectorizer
- import numpy as np
- import re
- from operator import itemgetter
- import pke
