from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import re
import textwrap
from operator import itemgetter

#Initialize Flask instance
app = Flask(__name__)

# Filepath for Alina: /Users/alina/Documents/GitHub/flask-example/
# Filepath for Migle: /Users/migle/myproject/flask-example/lyrics2.txt
f = open("/Users/migle/myproject/flask-example/lyrics2.txt")
op = f.read()
f.close()
documents = op.split(r'<|endoftext|>')

# tf-idf based search
tfv5 = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix = tfv5.fit_transform(documents).T.tocsr() # CSR: compressed sparse row format => order by terms
vocab = tfv5.vocabulary_

def tf_idf_search(tfv5, vocab, query):

    query = query.split()  # Split query in case it contains multiple terms
    if len(query) == 1:  # If query consists of only one term, operate on that
        query = ' '.join(map(str, query))
        if query != "":
            searchlist = []
            for word in vocab.keys():  # looping through all possible words in doc
                if re.search('^({}.+|{})'.format(query, query), word, re.IGNORECASE):  # if it finds words that start with the query...
                    searchlist.append(word)  # ...it appends them to our new list
            if searchlist != []:
                queryinput = ", "
                queryinput = queryinput.join(searchlist)  # joined members of list into a string

                query_vec5 = tfv5.transform([queryinput]).tocsc()  # CSC: compressed sparse column format
                hits = np.dot(query_vec5, sparse_matrix)

                total_docs = len(hits.nonzero()[1])
                matching_docs = hits.nonzero()[1]

                print("\nThe scores of the documents are:", np.array(hits[hits.nonzero()])[0], "\n")

                ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
                matches = []
                matchingdocs_list = list(map(itemgetter(1), ranked_scores_and_doc_ids)) #list of only matched doc numbers (in ranked order)
                print("Matching docs ranked:", matchingdocs_list)
                for search in searchlist:
                    print(search)
                    for doc in matchingdocs_list:
                        working_doc = documents[doc]
                        if search in working_doc:
                            index = working_doc.index(search)
                            matches.append(working_doc[index - 50: index + 50])
                        else:
                            continue
                return ranked_scores_and_doc_ids, hits, total_docs, matching_docs, queryinput, matches
        else:
            return None


    elif len(query) > 1:  # If query consists of multiple terms
        query = ' '.join(map(str, query))
        if query != "":
            query_vec5 = tfv5.transform([ query ]).tocsc()  # CSC: compressed sparse column format
            hits = np.dot(query_vec5, sparse_matrix)

            total_docs = len(hits.nonzero()[1])
            matching_docs = hits.nonzero()[1]

            ranked_scores_and_doc_ids = \
                sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)

            for score, i in ranked_scores_and_doc_ids:
                print("The score of", query,
                    "is {:.4f} in document #{:d}: {:s}".format(score, i, textwrap.shorten(documents[i], width=100)))

            return ranked_scores_and_doc_ids, hits, total_docs, matching_docs, matches
        else:
            None

#Function search() is associated with the address base URL + "/search"
@app.route('/search')
def search():

    #Get query from URL variable
    query = request.args.get('query')
    ranked_scores_and_doc_ids = []
    hits = []
    total_docs = []
    matching_docs = []
    queryinput = []
    matches = []

    results = tf_idf_search(tfv5, vocab, query)
    if results == None:
        ranked_scores_and_doc_ids = []
        hits = []
        total_docs = "0"
        matching_docs = "None"
        queryinput = "None"
    else:
        ranked_scores_and_doc_ids = results[0]
        hits = results[1]
        total_docs = results[2]
        matching_docs = results[3]
        queryinput = results[4]

    #Render index.html with matches variable
    return render_template('index.html', ranked_scores_and_doc_ids=ranked_scores_and_doc_ids, hits=hits, total_docs=total_docs, matching_docs=matching_docs, documents=documents, queryinput=queryinput, matches=matches)