""" This program reads a web page and ignores the HTML markup. It prints the text on the web page as plain text. """

from bs4 import BeautifulSoup
from urllib import request
from datetime import datetime

def main():

    url = "https://www.bbc.com/news/entertainment_and_arts"
    html = request.urlopen(url).read().decode('utf8')
    html[:60]

    raw = BeautifulSoup(html, 'html.parser')
    h3 = raw.find('h3').get_text()  # looking for the first h3 heading in a page, then stripping the HTML code
    p = raw.find(attrs={'gs-c-promo-summary gel-long-primer gs-u-mt nw-c-promo-summary'}).get_text()  # looking for the first instance of this ID in a page, then stripping the HTML code

    # adding a timestamp just for fun & to track content changes over time
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M)")

    # printing contents in plain text
    print("The top BBC News Entertainment & Arts story as of", timestampStr)
    print("")
    print("Title:", h3)
    print("Summary:", p)

main()
