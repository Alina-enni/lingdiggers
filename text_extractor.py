""" This program reads a web page and ignores the HTML markup. It tokenizes the text on the web page and prints the tokens. """

from nltk import word_tokenize
from bs4 import BeautifulSoup
from urllib import request

def main():

    url = "https://www.bbc.com/news/av/uk-60083200"
    html = request.urlopen(url).read().decode('utf8')
    html[:60]

    raw = BeautifulSoup(html, 'html.parser')
    h1 = raw.find('h1')  # looking for headings in a page
    p = raw.find_all('div', {'class': 'ssrcss-r2nzwz-RichTextContainer e5tfeyi1'})  # looking for all paragraphs with this ID in a page

    # printing and tokenizing
    print("Title:\n", word_tokenize(h1.text))  # print(h1.string) seems to give the same result
    print("Article text:")
    for line in p:
        print(word_tokenize(line.text))

main()