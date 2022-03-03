from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import re
import textwrap
from operator import itemgetter
import pke

{
    "python.pythonPath": "/Library/Frameworks/Python.framework/Versions/3.9/bin/python3",
}

#Initialize Flask instance
app = Flask(__name__)

# Filepath for Alina: /Users/alina/Documents/GitHub/flask-example/
# Filepath for Migle: /Users/migle/myproject/flask-example/lyrics2.txt
f = open("/Users/alina/Documents/GitHub/flask-example/lyrics2.txt")

op = f.read()
f.close()
documents = op.split(r'<|endoftext|>')

# tf-idf based search
tfv5 = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix = tfv5.fit_transform(documents).T.tocsr() # CSR: compressed sparse row format => order by terms
vocab = tfv5.vocabulary_

def extract_themes(extract_input):
    # initialize keyphrase extraction model, here TopicRank
    extractor = pke.unsupervised.TopicRank()

    # load the content of the document, here document is expected to be in raw
    # format (i.e. a simple text file) and preprocessing is carried out using spacy
    #file=open('/Users/alina/Documents/GitHub/lingdiggers/lyrics2.txt',encoding ='unicode_escape').read()
    extractor.load_document(input=extract_input, language='en')

    # keyphrase candidate selection, in the case of TopicRank: sequences of nouns
    # and adjectives (i.e. `(Noun|Adj)*`)
    extractor.candidate_selection()

    # candidate weighting, in the case of TopicRank: using a random walk algorithm
    extractor.candidate_weighting()

    # N-best selection, keyphrases contains the 10 highest scored candidates as
    # (keyphrase, score) tuples
    keyphrases = extractor.get_n_best(n=5)

    theme_dictionary = {}         # Put the keyphrases in a dictionary
    for i, y in keyphrases:
        theme_dictionary[y] = i
    return theme_dictionary


def tf_idf_search(tfv5, vocab, query):
    query = query.split()  # Split query in case it contains multiple terms
    if len(query) == 1:  # If query consists of only one term, operate on that
        query = ' '.join(map(str, query))
        if query != "":
            searchlist = []
            for word in vocab.keys():  # looping through all possible words in doc
                if re.search('^({}.+|{}|.+{}.+|.+{}$)'.format(query, query, query, query), word, re.IGNORECASE):  # if it finds words that start with the query...
                    searchlist.append(word)  # ...it appends them to our new list
            if searchlist != []:
                queryinput = ", "
                queryinput = queryinput.join(searchlist)  # joined members of list into a string

                query_vec5 = tfv5.transform([queryinput]).tocsc()  # CSC: compressed sparse column format
                hits = np.dot(query_vec5, sparse_matrix)

                total_docs = len(hits.nonzero()[1])
                matching_docs = hits.nonzero()[1]

                ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
                matches = []
                matchingdocs_list = list(
                    map(itemgetter(1), ranked_scores_and_doc_ids))  # list of only matched doc numbers (in ranked order)

                themedocs = " "
                for match in matching_docs:         # Theme extraction for the query
                    themedocs += documents[match]
                themes = extract_themes(themedocs)

                y = ("a, b",)
                count = tuple()
                count += y
                for search in searchlist:
                    for doc in matchingdocs_list:
                        working_doc = documents[doc]
                        artist_and_song = working_doc.split("\n")  # split on newline to discern artist and song names
                        for i in artist_and_song:  # to remove empty strings (newlines at the beginning of original doc + probably in between verses)
                            if re.match(r'^\s+$', i):
                                artist_and_song.remove(i)
                            else:
                                continue
                        artistname = artist_and_song[0]
                        songname = artist_and_song[1].replace(" Lyrics", "")
                        lyrics = ' '.join(artist_and_song[0:]).casefold()  # join actual lyrics back into one string
                        index = lyrics.find(
                            search)  # find the index of searched word #finds it in any part of word > changed regex above to fit this
                        tuple_doc_and_index = ("{}, {}".format(doc, index),)  # tuple of doc number and index of word
                        if index != -1:  # index returns -1 when the search does not exist in the string
                            if tuple_doc_and_index not in count:
                                count += ("{}, {}".format(doc, index),)
                                if index >= 50:  # not sure if still necessary
                                    matches += (("{} - {}".format(artistname, songname), "...{}...".format(lyrics[index - 50: index + 50])),)
                                elif index < 50:
                                    matches += (("{} - {}".format(artistname, songname), "...{}...".format(lyrics[0: index + 100])),)
                        else:
                            continue
                return ranked_scores_and_doc_ids, hits, total_docs, matching_docs, queryinput, matches, themes
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

            return ranked_scores_and_doc_ids, hits, total_docs, matching_docs
        else:
            None

#Function search() is associated with the address base URL + "/search"
@app.route('/search')
def search():

    #Get query from URL variable
    query = request.args.get('query')
    matches = []
    ranked_scores_and_doc_ids = []
    hits = []
    total_docs = []
    matching_docs = []
    queryinput = []
    themes = {}

        #If query exists (i.e. is not None)
    if query:
        #Look at each entry in the example data
        results = tf_idf_search(tfv5, vocab, query)

        if results == None:
            ranked_scores_and_doc_ids = []
            hits = []
            total_docs = "0"
            matching_docs = "None"
            queryinput = "None"
            matches = []
            themes = {}
        else:
            ranked_scores_and_doc_ids = results[0]
            hits = results[1]
            total_docs = results[2]
            matching_docs = results[3]
            queryinput = results[4]
            matches = results[5]
            themes = results[6]

    #Render index.html with matches variable
    return render_template('index.html', ranked_scores_and_doc_ids=ranked_scores_and_doc_ids, hits=hits, total_docs=total_docs, matching_docs=matching_docs, documents=documents, queryinput=queryinput, matches=matches, themes=themes)