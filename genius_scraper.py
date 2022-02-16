""" This is a scraping script for pulling lyrics from Genius using their own API """

GENIUS_API_TOKEN='OK93fmBOPEHDihuH2xD5IloNlps1sofo_FFX3viQGxSbvbBFOlM9nke5jc9D4rci'

# This is for Alina who uses Visual Studio Code which sometimes doesn't import libraries correctly
# except if I use this fix...
{
    "python.pythonPath": "/Library/Frameworks/Python.framework/Versions/3.9/bin/python3",
}

from lyricsgenius import Genius

file = open("lyrics2.txt", "a")
artists = ['Bob Dylan', 'Dua Lipa']
genius = Genius(GENIUS_API_TOKEN, skip_non_songs=False, remove_section_headers=True)

def get_lyrics(arr, k):
    c = 0
    for name in arr:
        try:
            songs = (genius.search_artist(name, max_songs=k)).songs
            s = [song.lyrics for song in songs]
            for i in s:
                file.write("Artist: " + name)
                file.write("\n")
                file.write(i)
                file.write("\n \n   <|endoftext|>   \n \n")
            c += 1
            print(f"Songs grabbed:{len(s)}")
        except:
            print(f"some exception at {name}: ", c)

get_lyrics(artists, 5)

file.close()
