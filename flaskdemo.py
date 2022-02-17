from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import re
import textwrap

#Initialize Flask instance
app = Flask(__name__)

# Filepath for Alina: /Users/alina/Documents/GitHub/flask-example/
f = open("/Users/alina/Documents/GitHub/flask-example/lyrics2.txt", encoding="utf-8")
op = f.read()
f.close()
documents = op.split(r'<|endoftext|>')

# tf-idf based search
tfv5 = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix = tfv5.fit_transform(documents).T.tocsr() # CSR: compressed sparse row format => order by terms

# Boolean search
cv = CountVectorizer(lowercase=True, binary=True, analyzer="word", token_pattern=r"(?u)\b\w+\b")
sparse_matrix2 = cv.fit_transform(documents)
sparse_td_matrix2 = sparse_matrix2.T.tocsr()
t2i = cv.vocabulary_  # Shorter notation: t2i = term-to-index

def tf_idf_search(tfv5, t2i, query):

    query = query.split()  # Split query in case it contains multiple terms
    if len(query) == 1:  # If query consists of only one term, operate on that
        query = ' '.join(map(str, query))
        if query != "":
            searchlist = []
            for word in t2i.keys():  # looping through all possible words in doc
                if re.search('^({}.+|{})'.format(query, query), word, re.IGNORECASE):  # if it finds words that start with the query...
                    searchlist.append(word)  # ...it appends them to our new list
            if searchlist != []:
                queryinput = ", "
                queryinput = queryinput.join(searchlist)  # joined members of list into a string
                print("\nThe following words were found:", queryinput)

                query_vec5 = tfv5.transform([queryinput]).tocsc()  # CSC: compressed sparse column format
                hits = np.dot(query_vec5, sparse_matrix)

                total_docs = len(hits.nonzero()[1])
                matching_docs = hits.nonzero()[1]

                print("\nThe scores of the documents are:", np.array(hits[hits.nonzero()])[0], "\n")

                ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
                for score, i in ranked_scores_and_doc_ids:
                    print("The score of", query,
                        "is {:.4f} in document #{:d}: {:s}".format(score, i, textwrap.shorten(documents[i], width=100)))
                return ranked_scores_and_doc_ids, hits, total_docs, matching_docs
            else:
                print("Sorry, no matches found in the collection.")
        else:
            print("Sorry, that document does not exist in the collection.")
    elif len(query) > 1:  # If query consists of multiple terms
        query = ' '.join(map(str, query))
        if query != "":
            query_vec5 = tfv5.transform([ query ]).tocsc()  # CSC: compressed sparse column format
            hits = np.dot(query_vec5, sparse_matrix)
            ranked_scores_and_doc_ids = \
                sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)

            total_docs = len(hits.nonzero()[1])
            matching_docs = hits.nonzero()[1]

            for score, i in ranked_scores_and_doc_ids:
                print("The score of", query,
                    "is {:.4f} in document #{:d}: {:s}".format(score, i, textwrap.shorten(documents[i], width=100)))
            return ranked_scores_and_doc_ids, hits, total_docs, matching_docs
        else:
            print("Sorry, that document does not exist in the collection.")

#Function search() is associated with the address base URL + "/search"
@app.route('/search')
def search():

    #Get query from URL variable
    query = request.args.get('query')
    ranked_scores_and_doc_ids = []
    hits = []
    total_docs = []
    matching_docs = []

        #If query exists (i.e. is not None)
    if query:
        #Look at each entry in the example data
        ranked_scores_and_doc_ids = tf_idf_search(tfv5, t2i, query)[0]
        hits = tf_idf_search(tfv5, t2i, query)[1]
        total_docs = tf_idf_search(tfv5, t2i, query)[2]
        matching_docs = tf_idf_search(tfv5, t2i, query)[3]

    #Render index.html with matches variable
    return render_template('index.html', ranked_scores_and_doc_ids=ranked_scores_and_doc_ids, hits=hits, total_docs=total_docs, matching_docs=matching_docs, documents=documents)