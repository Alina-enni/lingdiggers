""" This is a scraping script for pulling lyrics from Genius using their own API """

GENIUS_API_TOKEN='OK93fmBOPEHDihuH2xD5IloNlps1sofo_FFX3viQGxSbvbBFOlM9nke5jc9D4rci'

# This is for Alina who uses Visual Studio Code which sometimes doesn't import libraries correctly
# except if I use this fix...
{
    "python.pythonPath": "/Library/Frameworks/Python.framework/Versions/3.9/bin/python3",
}

from lyricsgenius import Genius

file = open("lyrics2.txt", "a", encoding="utf-8")
artists = ['Coldplay', 'Tori Amos', 'Blur', 'Beatles', 'Michael Jackson', 'Queen',
           'Taylor Swift', 'Blue October', 'Porcupine Tree', 'Muse', 'Annie Lennox',
           'Frank Sinatra', 'David Bowie', 'Elton John', 'Bombay Bicycle Club', 'The Kinks',
           'Bananarama', 'Franz Ferdinand', 'Kate Bush', 'Mos Def', 'Fleetwood Mac', 'The Weeknd',
           'Imagine Dragons', 'Radiohead', 'Billie Eilish', 'Jackson 5', 'Chet Baker']
genius = Genius(GENIUS_API_TOKEN, skip_non_songs=False, remove_section_headers=True)

def get_lyrics(artists, k):
    artist = input("Name of artist to add to lyrics file:")
    c = 0
    if artist not in artists:
        try:
            songs = (genius.search_artist(artist, max_songs=k)).songs
            s = [song.lyrics for song in songs]
            for i in s:
                file.write(artist)
                file.write("\n")
                file.write(i)
                file.write("\n \n   <|endoftext|>   \n \n")
            c += 1
            print(f"Songs grabbed:{len(s)}")
        except:
            print(f"some exception at {artist}: ", c)
    else:
        print("We already have that!")

get_lyrics(artists, 5)

file.close()
