import pke
# Comment out the part below if it is not needed for you. This fixes the VSC problem of not importing libraries.
{
    "python.pythonPath": "/Library/Frameworks/Python.framework/Versions/3.9/bin/python3",
}

# initialize keyphrase extraction model, here TopicRank
extractor = pke.unsupervised.TopicRank()

# load the content of the document, here document is expected to be in raw
# format (i.e. a simple text file) and preprocessing is carried out using spacy
file=open('/Users/alina/Documents/GitHub/lingdiggers/lyrics2.txt',encoding ='unicode_escape').read()
extractor.load_document(input=file, language='en')

# keyphrase candidate selection, in the case of TopicRank: sequences of nouns
# and adjectives (i.e. `(Noun|Adj)*`)
extractor.candidate_selection()

# candidate weighting, in the case of TopicRank: using a random walk algorithm
extractor.candidate_weighting()

# N-best selection, keyphrases contains the 10 highest scored candidates as
# (keyphrase, score) tuples
keyphrases = extractor.get_n_best(n=10)

dictionary = {}         # Put the keyphrases in a dictionary
for i, y in keyphrases:
    dictionary[y] = i

print()
print("The themes found in this index are:")    # Print the keys and values to show all the keyphrases found
print()
for key in dictionary:
    print(dictionary[key], "- with the score: ", key)
print()