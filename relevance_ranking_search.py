from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
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

# tf-idf based search
tfv5 = TfidfVectorizer(lowercase=True, sublinear_tf=True, use_idf=True, norm="l2")
sparse_matrix = tfv5.fit_transform(documents).T.tocsr() # CSR: compressed sparse row format => order by terms

# Boolean search
cv = CountVectorizer(lowercase=True, binary=True, analyzer="word", token_pattern=r"(?u)\b\w+\b")
sparse_matrix2 = cv.fit_transform(documents)
sparse_td_matrix2 = sparse_matrix2.T.tocsr()
t2i = cv.vocabulary_  # Shorter notation: t2i = term-to-index

# Operators and/AND, or/OR, not/NOT become &, |, 1 -
# Parentheses are left untouched
# Everything else interpreted as a term and fed through td_matrix2[t2i["..."]]
d = {"and": "&", "AND": "&",
    "or": "|", "OR": "|",
    "not": "1 -", "NOT": "1 -",
    "(": "(", ")": ")"}          # Operator replacements

def rewrite_token(t):
    return d.get(t, 'sparse_td_matrix2[t2i["{:s}"]].todense()'.format(t)) # Make retrieved rows dense
    
def rewrite_query(query): # Rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

def test_query(query):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query))
    print("Matching:", eval(rewrite_query(query))) # Eval runs the string as a Python command
    print()

def print_contents(query, boolean):
    if query != "UKN":
        hits_matrix = eval(rewrite_query(query))
        hits_list = list(hits_matrix.nonzero()[1])
        if len(hits_list) == 1 and boolean == 0:
            print(len(hits_list) ,"document found")
        elif len(hits_list) > 1 and boolean == 0:
            print(len(hits_list) ,"documents found")
        elif len(hits_list) == 1 and boolean == 1:
            print((len(hits_list)-1) ,"document found")
        elif len(hits_list) > 1 and boolean == 1:
            print((len(hits_list)-1),"documents found")
        
        print()
        if boolean == 0:
            for i, doc_idx in enumerate(hits_list, start=1):
                print("Matching doc #{:d}: {:s}".format(i, textwrap.shorten(documents[doc_idx], width=100)))

        elif boolean == 1:
            hits_list = hits_list[:-1]
            for i, doc_idx in enumerate(hits_list, start=1):
                print("Matching doc #{:d}: {:s}".format(i, textwrap.shorten(documents[doc_idx], width=100)))

    elif query == "UKN":
        print("Sorry, that document does not exist in the collection.")

search_type = 0
while search_type != 3:
    search_type = int(input("\nType 1 for Boolean search, 2 for tf-idf based search or 3 to quit: "))

    # tf-idf based search
    if search_type == 2:
        queryinput = input("Type your query: ")
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
        
    # Boolean search
    elif search_type == 1:
        queryinput = input("Type your query: ").casefold()
        queryinput = queryinput.split()    # Split query in case it contains multiple terms
        if len(queryinput) == 1:    # If query consists of only one term, operate on that
            boolean = 0
            queryinput = ' '.join(map(str, queryinput))
            if queryinput in t2i.keys():
                print_contents(queryinput, boolean)
                print()
            elif queryinput not in t2i.keys() and queryinput != "":
                queryinput = "UKN"
                t2i[queryinput] = 0
                print_contents(queryinput, boolean)
                print()

        elif len(queryinput) > 1:       # If query consists of multiple terms, e.g. "NOT example"
            i = 0
            boolean = 0
            operators = 0               # Counter variable for keeping track of operators in the query
            multiquery = []
            while i < len(queryinput): 
                if queryinput[i] in d.keys():           # Check if term found in operators
                    multiquery.append(queryinput[i])
                    operators += 1
                    if queryinput[i] == "not" or queryinput == "NOT":
                        boolean = 1
                elif queryinput[i] in t2i.keys():       # Check if term found in documents
                    multiquery.append(queryinput[i])
                elif queryinput[i] not in t2i.keys():   # If there's an unknown term
                    t2i["UKN"] = 0
                    multiquery.append("UKN")
                i += 1
                
            # Query only run if it consists of a single search term or multiple separated by an operator
            if operators == 0 and len(queryinput) > 1:
                print("Please use an operator to separate multiple search terms. The accepted operators are AND and OR.")
            elif operators != 0 or len(queryinput) == 1:
                multiquery = ' '.join(map(str, multiquery))
                print_contents(multiquery, boolean)
    
    elif search_type != 1 and search_type != 2 and search_type != 3:
        print("\nThat is not a valid choice!")

if search_type == 3:
    print()
    print("Quitting the program. Goodbye!")