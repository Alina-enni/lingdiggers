""" This program reads a web page and ignores the HTML markup. It tokenizes the text on the web page and prints the tokens. """

from nltk import word_tokenize
from bs4 import BeautifulSoup
from urllib import request

def main():

    url = "https://www.bbc.com/news/av/uk-60083200"
    html = request.urlopen(url).read().decode('utf8')
    html[:60]

    raw = BeautifulSoup(html, 'html.parser').get_text()
    tokens = word_tokenize(raw)
    tokens = tokens[0:126]

    print()
    print(tokens)

main()