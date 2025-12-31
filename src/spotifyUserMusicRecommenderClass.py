import csv
import os
import math
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from ProfileClass import Profile

class spotifyUserMusicRecommender:
    def __init__(self, user, audioFeaturesCsv, musicMetadataCsv, spotify_client):
        profile = Profile(user)
        self.user = str(profile.username)
        self.sp = spotify_client
        self.audioFeaturesCsv = audioFeaturesCsv
        self.musicMetadataCsv = musicMetadataCsv
        self.songFeatures, self.musicMetadata = self.loadSongFeatures(audioFeaturesCsv, musicMetadataCsv)
        self.userVector = []

    def loadSongFeatures(self, audioFeaturesCsv, musicMetadataCsv):
        songFeatures = {}
        musicMetadata = {}

        with open(audioFeaturesCsv, newline='', encoding='utf-8') as file:#Lines 27-54 CVS extractions inspired by 'https://www.geeksforgeeks.org/working-csv-files-python/' and ChatGPT
            reader = csv.DictReader(file)
            for row in reader:
                title = row['Title']
                features = [
                    self.safeFloatConversion(row['Popularity']),
                    self.safeFloatConversion(row['Energy']),
                    self.safeFloatConversion(row['Danceability']),
                    self.safeFloatConversion(row['Positiveness']),
                    self.safeFloatConversion(row['Speechiness']),
                    self.safeFloatConversion(row['Liveness']),
                    self.safeFloatConversion(row['Acousticness']),
                    self.safeFloatConversion(row['Instrumentalness']),
                    self.safeFloatConversion(row['Tempo'])
                ]
                songFeatures[title] = {'features': features}

        with open(musicMetadataCsv, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row['Title']
                artist = row['Artist']
                musicMetadata[title] = {
                    'artist': artist,
                    'city': row['City'],
                    'decade': row['Decade']
                }
        
        return songFeatures, musicMetadata
    
    def safeFloatConversion(self, value):   #debug suggestion by CHATGPT
        try:
            return float(value)
        except ValueError:
            return 0.0
    
    def cosineSimilarity(self, vector1, vector2):
        print(vector1)
        print(vector2)
        dotProduct = 0
        for i in range(len(vector1)):
            dotProduct += vector1[i] * vector2[i]
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(b * b for b in vector2))
        
        if magnitude1 > 0 and magnitude2 > 0:
            return dotProduct / (magnitude1 * magnitude2)
        else:
            return 0

    def getTopCompatibleSongs(self, userVectors, quizVector, topN=10, excludeHistory=True, quizWeight=2):
        if isinstance(userVectors, list) and all(isinstance(vec, float) for vec in userVectors):
            userVectors = [userVectors]

        if not isinstance(quizVector, list): #debug suggestion by ChatGPT
            raise TypeError("quizVector must be a list.")

        print(f"userVectors: {userVectors}")
        print(f"quizVector: {quizVector}")

        trackFeatures = {}
        userProfile = Profile(self.user)
        userData = userProfile.loadingData()

        try: #debug suggestion by ChatGPT
            usedSongs = {song.strip().lower() for song in userData.get(self.user, {}).get('recommendedSongs', '').split(';') if song.strip()}
        except KeyError:
            usedSongs = set()

        newRecommendations = []
        for trackName, data in self.songFeatures.items():
            if excludeHistory and trackName.lower() in usedSongs:
                continue

            if trackName not in self.musicMetadata:
                continue

            features = data['features']
            totalSimilarity = 0
            totalWeight = 0

            for pastVector in userVectors:
                similarity = self.cosineSimilarity(pastVector, features)
                totalSimilarity += similarity
                totalWeight += 1

            quizSimilarity = self.cosineSimilarity(quizVector, features)
            totalSimilarity += quizSimilarity * quizWeight
            totalWeight += quizWeight
            avgSimilarity = totalSimilarity / totalWeight

            metadata = self.musicMetadata[trackName]
            trackFeatures[trackName] = {
                "score": avgSimilarity * 100,
                "artist": metadata.get('artist', 'Unknown Artist'),
                "city": metadata.get('city', 'Unknown City'),
                "decade": metadata.get('decade', 'Unknown Decade')
            }

            if trackName.lower() not in usedSongs:
                newRecommendations.append(trackName)

        maxScore = max(track["score"] for track in trackFeatures.values()) if trackFeatures else 1
        for features in trackFeatures.values():
            features["score"] = (features["score"] / maxScore) * 100

        sortedTracks = sorted(trackFeatures.items(), key=lambda x: x[1]["score"], reverse=True) #Inspired by 112 Lecture
        topRecommendations = sortedTracks[:topN]

        topSongs = [track[0] for track in topRecommendations]
        userProfile.updateRecommendedSongs(topSongs, username=self.user)
        print(topSongs)

        return topRecommendations

    def getTopCompatibleSongsWithDetails(self, userVectors, quizVector, topN=10, excludeHistory=True, quizWeight=2):
        topRecommendations = self.getTopCompatibleSongs(userVectors, quizVector, topN, excludeHistory, quizWeight)
        detailedRecommendations = []
        with open('imageUrls.csv', newline='', encoding='utf-8') as file: #Lines 140 - 146 use of CVS extractions inspired by 'https://www.geeksforgeeks.org/working-csv-files-python/' and ChatGPT
            imageReader = csv.DictReader(file)
            imageData = {row['Title'].strip().lower(): row['ImageURL'] for row in imageReader}

        with open('cleanedSongs.csv', newline='', encoding='utf-8') as file:
            songReader = csv.DictReader(file)
            songData = {row['Title'].strip().lower(): row['File Path'] for row in songReader}

        for trackName, trackData in topRecommendations:
            trackTitle = trackName.strip().lower()
            imageUrl = imageData.get(trackTitle, None)
            filePath = songData.get(trackTitle, None)

            trackData['imageUrl'] = imageUrl
            trackData['file_path'] = filePath

            detailedRecommendations.append((trackName, trackData))

        return detailedRecommendations

    def findMostCompatibleCityDecade(self, compatibleSongs):
        decadeScores = {}
        cityScores = {}
        cityDecadeScores = {}

        for i, trackData in compatibleSongs:
            decade = trackData.get('decade', 'Unknown Decade')
            city = trackData.get('city', 'Unknown City')
            score = trackData.get('score', 0)

            if decade not in decadeScores:
                decadeScores[decade] = 0
            decadeScores[decade] += score

            if city not in cityScores:
                cityScores[city] = 0
            cityScores[city] += score

            cityDecadeKey = (city, decade)
            if cityDecadeKey not in cityDecadeScores:
                cityDecadeScores[cityDecadeKey] = 0
            cityDecadeScores[cityDecadeKey] += score

        mostCompatibleDecade = max(decadeScores, key=decadeScores.get, default='Unknown Decade')
        mostCompatibleCity = max(cityScores, key=cityScores.get, default='Unknown City')
        mostCompatibleCityDecade = max(cityDecadeScores, key=cityDecadeScores.get, default=('Unknown City', 'Unknown Decade'))

        return mostCompatibleDecade, mostCompatibleCity, mostCompatibleCityDecade

    def getSpotifyTrackIds(self, trackNames):       #Lines 189-206 inspired by spotipy (in citation doc)
        trackIds = []
        for trackName in trackNames:
            if trackName in self.songFeatures:
                artist = self.musicMetadata.get(trackName, {}).get('artist', '')
                searchQuery = f"{trackName} {artist}" if artist else trackName
                results = self.sp.search(q=searchQuery, limit=1, type='track')
                
                if results['tracks']['items']:
                    trackIds.append(results['tracks']['items'][0]['id'])
        return trackIds

    def createPlaylist(self, userId, playlistName="Top 10 HOUSE RADIOOOOO Recommendations Cosine"):
        playlist = self.sp.user_playlist_create(userId, playlistName, public=False)
        return playlist['id']

    def addTracksToPlaylist(self, playlistId, trackIds):
        self.sp.playlist_add_items(playlistId, trackIds)

    def recommendForUser(self, quizVector, topN=10, importing='no', quizWeight=2):
        profile = Profile(self.user)
        userData = profile.loadingData().get(self.user, {})

        pastAnswers = userData.get('pastAnswers', '')
        pastVectors = [list(map(float, vec.split(','))) for vec in pastAnswers.split('|')] if pastAnswers else [] #optimized code using ChatGPT

        topRecommendations = self.getTopCompatibleSongs(pastVectors, quizVector, topN, quizWeight=quizWeight)
        recommendedTracks = [track[0] for track in topRecommendations]
        profile.updatePastAnswers(newVector=quizVector, newRecommendations=recommendedTracks)

        if importing == 'yes':
            trackIds = self.getSpotifyTrackIds(recommendedTracks)
            userId = self.sp.current_user()['id']
            playlistId = self.createPlaylist(userId)
            self.addTracksToPlaylist(playlistId, trackIds)
            print(f"Playlist created with {topN} tracks.")