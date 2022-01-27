from sklearn.feature_extraction.text import CountVectorizer

def main():

    documents = ["This is a silly example",
                "A better example",
                "Nothing to see here",
                "This is a great and long example"]

    cv = CountVectorizer(lowercase=True, binary=True)
    sparse_matrix = cv.fit_transform(documents)

    print("Term-document matrix: (?)\n")
    print(sparse_matrix)

    dense_matrix = sparse_matrix.todense()

    print("Term-document matrix: (?)\n")
    print(dense_matrix)

    td_matrix = dense_matrix.T   # .T transposes the matrix

    print("Term-document matrix:\n")
    print(td_matrix)

    t2i = cv.vocabulary_  # shorter notation: t2i = term-to-index
    print("Query: example")
    print(td_matrix[t2i["example"]])

main()