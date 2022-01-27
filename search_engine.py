from sklearn.feature_extraction.text import CountVectorizer

documents = ["This is a silly example",
            "A better example",
            "Nothing to see here",
            "This is a great and long example"]

cv = CountVectorizer(lowercase=True, binary=True, analyzer="word", token_pattern=r"(?u)\b\w+\b")
sparse_matrix = cv.fit_transform(documents)
sparse_td_matrix = sparse_matrix.T.tocsr()
t2i = cv.vocabulary_  # shorter notation: t2i = term-to-index

# Operators and/AND, or/OR, not/NOT become &, |, 1 -
# Parentheses are left untouched
# Everything else interpreted as a term and fed through td_matrix[t2i["..."]]
d = {"and": "&", "AND": "&",
    "or": "|", "OR": "|",
    "not": "1 -", "NOT": "1 -",
    "(": "(", ")": ")"}          # operator replacements

def rewrite_token(t):
    return d.get(t, 'sparse_td_matrix[t2i["{:s}"]].todense()'.format(t)) # Make retrieved rows dense
    
def rewrite_query(query): # rewrite every token in the query
    return " ".join(rewrite_token(t) for t in query.split())

def test_query(query):
    print("Query: '" + query + "'")
    print("Rewritten:", rewrite_query(query))
    print("Matching:", eval(rewrite_query(query))) # Eval runs the string as a Python command
    print()

def print_contents(query):
    if query != "UKN":
        hits_matrix = eval(rewrite_query(query))
        print("Matching documents as vector (it is actually a matrix with one single row):", hits_matrix)
        print("The coordinates of the non-zero elements:", hits_matrix.nonzero())
        hits_list = list(hits_matrix.nonzero()[1])
        print(hits_list)
        for i, doc_idx in enumerate(hits_list):
            print("Matching doc #{:d}: {:s}".format(i, documents[doc_idx]))
    elif query == "UKN":
        print("Sorry, that document does not exist in the collection.")

queryinput = "0"
while queryinput != []:
    queryinput = input("Type your query: ").split()    # Split query in case it contains multiple terms

    if len(queryinput) == 1:    # If query consists of only one term, operate on that
        queryinput = ' '.join(map(str, queryinput))
        if queryinput in t2i.keys():
            test_query(queryinput)
            print_contents(queryinput)
            print()

        elif queryinput not in t2i.keys() and queryinput != "":
            queryinput = "UKN"
            t2i[queryinput] = 0
            test_query(queryinput)
            print_contents(queryinput)
            print()

    elif len(queryinput) > 1:       # If query consists of multiple terms, e.g. "NOT example"
        i = 0
        multiquery = []
        while i < len(queryinput): 
            if queryinput[i] in d.keys():           # Check if term found in operators
                multiquery.append(queryinput[i])
            elif queryinput[i] in t2i.keys():       # Check if term found in the documents
                multiquery.append(queryinput[i])
            elif queryinput[i] not in t2i.keys():   # If there's an unknown term
                t2i["UKN"] = 0
                multiquery.append("UKN")
            i += 1

        multiquery = ' '.join(map(str, multiquery))
        print(t2i.keys())
        test_query(multiquery)
        print_contents(multiquery)

if queryinput == []:
    print()
    print("Goodbye!")