# lingdiggers
Project for the Building NLP Applications course

We have created a search engine, that searches through a (small) song lyrics database and presents all occurences of a query along with the artist and song name. Results are shortened to show only the query in context (and not the whole song).
Our engine supports single word and multiword queries. With single word queries it looks for an occurence anywhere within a word; e.g. if a query is 'way', our engine searches for words such as 'way', 'ways', 'away' etc. With multiword queries the engine searches only for the specific words in the query; e.g. 'fix you' shows results with 'fix' and 'you'.
As we are using the tf-idf method, the results in both cases are ranked and presented in descending order.

To use the search engine, 3 files are needed:
- flaskdemo.py should be located in the flask folder
- lyrics2.txt is the (small) lyrics database and should be located where the python file is.
- index.html located in the templates folder.
