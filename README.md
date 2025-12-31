# house-radiooooo
Designed and built an interactive music discovery app focused on house music across cities and decades. Implemented content-based recommendation using Spotify audio features, integrated Spotify’s API for playlist creation, and built an interactive world map interface. (Developed as part of CMU 15-112: Fundamentals of Programming)

readme.txt

Project Title: HOUSE RADIOOOOO
You are tuning in to HOUSE RADIOOOOO!

Project Descrption:
What is HOUSE RADIOOOOO?
This is my 112 term project that is an interactive music application. With use of spotipy, the Spotify API, users can create curated playlists based on quiz inputs (song audio features) as well as import their recommended songs to their spotify account. There is also an interactive map that displays the most significant cities related to house music. Users are allowed to select different cities and decades, play songs to the corresponding inputs, and save them. User profiles are saved, so when logged in, users are allowed to view their stats, such as liked songs and preferences from past sessions.

How to run:
Make sure to have these installed packages:
- pygame, csv, os, pandas, pillow, plotly, spotipy, cmu_graphics

To install, in terminal:
pip install cmu-graphics
pip install spotipy
pip install pygame
pip install plotly
pip install pandas
pip install pillow

To run (use main.py):
1. Make sure all files ---- media (mp3s, images), source (csvs) --- class are in src folder *****
2. First authenticate yourself as a user (follow terminal instructions)
3. Now you should be tuned in to HOUSE RADIOOOOO

****Files to have:
Csvs:
1. 'absoluteCleanedSongs.csv'
2. 'absoluteImageUrls.csv'
3. 'profiles.csv'

Mp3:
1. Amsterdam, Barcelona, Berlin, Bogota, CapeTown, Chicago, Detroit, Ibiza, Johannesburg, Lagos, London, LosAngeles, NewYork, Paris, Rio, Stockholm
2. 'allThatJunk'.mp3
3. 'houseIntro'.mp3

Images:
1. 'raw_map.png'
2. 'thankYouElaine.png'
3. 'user_similarity_map.png'
4. 'SignOut.png'
5. 'album_cover.png'

Classes:
1. ProfileClass.py
2. MapGeneratorClass.py
3. spotifyUserMusicRecommenderClass.py

