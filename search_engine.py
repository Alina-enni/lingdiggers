from sklearn.feature_extraction.text import CountVectorizer

def main():

    documents = ["This is a silly example",
                "A better example",
                "Nothing to see here",
                "This is a great and long example"]

    cv = CountVectorizer(lowercase=True, binary=True)
    sparse_matrix = cv.fit_transform(documents)

    dense_matrix = sparse_matrix.todense()

    td_matrix = dense_matrix.T   # .T transposes the matrix

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

    test_query("example AND NOT nothing")
    test_query("NOT example OR great")
    test_query("( NOT example OR great ) AND nothing") # AND, OR, NOT can be written either in ALLCAPS
    test_query("( not example or great ) and nothing") # ... or all small letters
    test_query("not example and not nothing")


main()