from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import textwrap

# Filepath for Alina: /Users/alina/Documents/GitHub/lingdiggers/
f = open("100articles.txt", encoding="utf-8")
op = f.read()
f.close()
op = re.sub(r'\n', r'', op)
documents = op.split(r'</article>')
remove_html = re.compile(r"<.*?>")
documents = [remove_html.sub(' ', a).strip() for a in documents]

tfv5 = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix = tfv5.fit_transform(documents).T.tocsr() # CSR: compressed sparse row format => order by terms

queryinput = "0"
while queryinput != "":
    queryinput = input("Type your query: ")

    if queryinput != "":
        # The query vector is a horizontal vector, so in order to sort by terms, we need to use CSC
        query_vec5 = tfv5.transform([queryinput]).tocsc() # CSC: compressed sparse column format
        hits = np.dot(query_vec5, sparse_matrix)
        print()
        print("The matching documents are:", hits.nonzero()[1])
        print()
        print("The scores of the documents are:", np.array(hits[hits.nonzero()])[0])
        print()

        ranked_scores_and_doc_ids = sorted(zip(np.array(hits[hits.nonzero()])[0], hits.nonzero()[1]), reverse=True)
        for score, i in ranked_scores_and_doc_ids: 
            print("The score of", queryinput, "is {:.4f} in document: {:s}".format(score, textwrap.shorten(documents[i], width=100)))
        print()

if queryinput == "":
    print()
    print("Quitting the program. Goodbye!")