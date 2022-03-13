from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
from operator import itemgetter
import pke

#Initialize Flask instance
app = Flask(__name__)

f = open("YOUR_FILEPATH/lyrics2.txt")       # Use accurate file path to open your song lyric index (.txt file)
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
    extractor.load_document(input=extract_input, language='en')
    extractor.candidate_selection()
    extractor.candidate_weighting()
    # N-best selection, keyphrases contains the 10 highest scored candidates as (keyphrase, score) tuples
    keyphrases = extractor.get_n_best(n=5)
    theme_dictionary = {}                   # Put the keyphrases in a dictionary

    for i, y in keyphrases:
        theme_dictionary[y] = i
    return theme_dictionary

def tf_idf_search(tfv5, vocab, query):
    query = query.split()
    if len(query) == 1:  # If query consists of only one term
        query = ' '.join(map(str, query))
        if query != "":
            searchlist = []
            for word in vocab.keys():  # Loop through all possible words in the doc
                if re.search('^({}.+|{}|.+{}.+|.+{}$)'.format(query, query, query, query), word, re.IGNORECASE):  # If we find words that start with the query...
                    searchlist.append(word)  # ...append them to list

            if searchlist != []:
                queryinput = ", "
                queryinput = queryinput.join(searchlist)

                query_vec5 = tfv5.transform([queryinput]).tocsc()  # CSC: compressed sparse column format
                hits = np.dot(query_vec5, sparse_matrix)

                total_docs = len(hits.nonzero()[1])
                matching_docs = hits.nonzero()[1]

                ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
                matches = []
                matchingdocs_list = list(
                    map(itemgetter(1), ranked_scores_and_doc_ids))  # Only matched doc numbers (in ranked order)

                themedocs = " "
                for match in matching_docs:         # Theme extraction for the query
                    themedocs += documents[match]
                themes = extract_themes(themedocs)

                count = tuple()
                for doc in matchingdocs_list:
                    working_doc = documents[doc]
                    for search in searchlist:
                        artist_and_song = working_doc.split("\n")  # Split on the newline to discern artist and song name
                        for i in artist_and_song:  # Remove empty strings
                            if re.match(r'^\s+$', i):
                                artist_and_song.remove(i)
                            else:
                                continue
                        if len(artist_and_song[0]) == 1 and artist_and_song[0][0] == ' ':
                            artist_and_song.pop(0)
                        artistname = artist_and_song[0]
                        songname = artist_and_song[1].replace(" Lyrics", "")
                        video_code = artist_and_song[-1]
                        lyrics = " " + ' '.join(artist_and_song[0:-2]).casefold()  # Join lyrics back into one string
                        if search in artistname.casefold():
                            pass
                        else:
                            search = " " + search + " "
                        index = lyrics.find(search)  # Find the index of the searched word

                        tuple_doc_and_index = ("{}, {}".format(doc, index),) 
                        if index != -1:  # Returns -1 when the search does not exist in the string
                            if tuple_doc_and_index not in count:
                                count += ("{}, {}".format(doc, index),)
                                if index >= 50:
                                    matches += (("{} - {}".format(artistname, songname), "...{}...".format(lyrics[index - 50: index + 50]), "{}".format(video_code)),)
                                elif index < 50:
                                    matches += (("{} - {}".format(artistname, songname), "...{}...".format(lyrics[0: index + 100]), "{}".format(video_code)),)
                        else:
                            continue
                return ranked_scores_and_doc_ids, hits, total_docs, matching_docs, queryinput, matches, themes
        else:
            return None

    elif len(query) > 1:  # If query consists of multiple terms
        query = ' '.join(map(str, query))
        if query != []:
            searchlist = []
            searches = query.split()
            for i in searches:
                for word in vocab.keys():  # Loop through all possible words in the doc
                    if re.search('^({}.+|{}|.+{}.+|.+{}$)'.format(i, i, i, i), word, re.IGNORECASE):  # If we find words that start with the query...
                        searchlist.append(word)  # ...append to new list
            
            if searchlist != []:
                queryinput = ", "
                queryinput = queryinput.join(searchlist)

                query_vec5 = tfv5.transform([ query ]).tocsc()  # CSC: compressed sparse column format
                hits = np.dot(query_vec5, sparse_matrix)

                total_docs = len(hits.nonzero()[1])
                matching_docs = hits.nonzero()[1]

                ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
                matches = []
                matchingdocs_list = list(
                    map(itemgetter(1), ranked_scores_and_doc_ids))  # Only matched doc numbers (in ranked order)

                themedocs = " "
                for match in matching_docs:         # Theme extraction for the query
                    themedocs += documents[match]
                themes = extract_themes(themedocs)

                count = tuple()
                for doc in matchingdocs_list:
                    working_doc = documents[doc]
                    for search in query:
                        search = " " + search + " "
                        artist_and_song = working_doc.split("\n")  # Split on the newline to discern artist and song name
                        for i in artist_and_song:  # Remove empty strings
                            if re.match(r'^\s+$', i):
                                artist_and_song.remove(i)
                            else:
                                continue
                        if len(artist_and_song[0]) == 1 and artist_and_song[0][0] == ' ':
                            artist_and_song.pop(0)
                        artistname = artist_and_song[0]
                        songname = artist_and_song[1].replace(" Lyrics", "")
                        video_code = artist_and_song[-1]
                        lyrics = " " + ' '.join(artist_and_song[0:-2]).casefold()  # Join lyrics back into one string
                        index = lyrics.find(search)  # Find the index of the searched word
                        tuple_doc_and_index = ("{}, {}".format(doc, index),)
                        if index != -1:  # Returns -1 when the search does not exist in the string
                            if tuple_doc_and_index not in count:
                                count += ("{}, {}".format(doc, index),)
                                if index >= 50: 
                                    matches += (("{} - {}".format(artistname, songname), "...{}...".format(lyrics[index - 50: index + 50]), "{}".format(video_code)),)
                                elif index < 50:
                                    matches += (("{} - {}".format(artistname, songname), "...{}...".format(lyrics[0: index + 100]), "{}".format(video_code)),)
                        else:
                            continue
                return ranked_scores_and_doc_ids, hits, total_docs, matching_docs, queryinput, matches, themes
        else:
            return None

#Function search() is associated with the address base URL + "/search"
@app.route('/search')
def search():

    #Get query from URL variable
    query = request.args.get('query')
    matches = []
    ranked_scores_and_doc_ids = []
    hits = []
    total_docs = "0"
    matching_docs = ""
    queryinput = ""
    themes = {}

    #If query exists (i.e. is not None)
    if query:
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