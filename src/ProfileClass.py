import csv
class Profile:
    def __init__(self, username, profilesData='profiles.csv'):
        self.username = username
        self.profilesData = profilesData

    def loadingData(self): #function made using CVS extractions help inspired by 'https://www.geeksforgeeks.org/working-csv-files-python/' and ChatGPT
        userInfo = {}
        with open(self.profilesData, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row['username']
                userInfo[username] = {
                    'pastAnswers': row['pastAnswers'],
                    'recommendedSongs': row['recommendedSongs'],
                    'likedSongs': row['likedSongs']
                }
        return userInfo

    def addUser(self, username=None, pastAnswers="", recommendedSongs="", likedSongs=""):
        username = username or self.username
        userInfo = self.loadingData()

        if username in userInfo:
            print(f"User {username} already exists. Skipping addition.")
            return

        userInfo[username] = {
            "pastAnswers": pastAnswers,
            "recommendedSongs": recommendedSongs,
            "likedSongs": likedSongs
        }
        self._rewrite_csv(userInfo)
        print(f"User {username} added successfully.")

    def updatePastAnswers(self, newVector, newRecommendations=None, username=None): #function made using CVS extractions help inspired by 'https://www.geeksforgeeks.org/working-csv-files-python/' and ChatGPT
        userInfo = {}
        username = username or self.username
        print(f"Updating past answers for user: {username}")
        userInfo = self.loadingData()

        if username in userInfo:
            existingVectors = userInfo[username].get('pastAnswers', '')
            if existingVectors:
                existingVectors = [list(map(float, vec.split(','))) for vec in existingVectors.split('|')] #optimized using CHAT GPT
            else:
                existingVectors = []

            if newVector not in existingVectors:
                existingVectors.append(newVector)

            userInfo[username]['pastAnswers'] = '|'.join(
                ','.join(map(str, vec)) for vec in existingVectors
            )
        else:
            print(f"User {username} not found. Adding them.")
            self.addUser(
                username=username,
                pastAnswers=','.join(map(str, newVector)),
                recommendedSongs=';'.join(newRecommendations) if newRecommendations else ''
            )
            return

        if newRecommendations:
            existingSongs = userInfo[username].get('recommendedSongs', '').split(';')
            existingSongs = {song.strip().lower() for song in existingSongs if song.strip()}
            for song in newRecommendations:
                existingSongs.add(song.lower())
            userInfo[username]['recommendedSongs'] = ';'.join(sorted(existingSongs))

        self._rewrite_csv(userInfo)

    def _rewrite_csv(self, userInfo): #inspired by 'https://www.geeksforgeeks.org/working-csv-files-python/'
        with open(self.profilesData, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["username", "pastAnswers", "recommendedSongs", "likedSongs"])
            writer.writeheader()
            for user, data in userInfo.items():
                writer.writerow({
                    "username": user,
                    "pastAnswers": data.get('pastAnswers', ''),
                    "recommendedSongs": data.get('recommendedSongs', ''),
                    "likedSongs": data.get('likedSongs', '')
                })

    def updateRecommendedSongs(self, newSongs, username=None):
        username = username or self.username
        if not isinstance(username, str): #debug suggestion by CHAT GPT
            raise TypeError(f"Expected username to be a string, got {type(username)} instead.")

        userInfo = self.loadingData()

        if username in userInfo:
            existingSongs = userInfo[username].get('recommendedSongs', '').split(';')
            existingSongs = {song.strip().lower() for song in existingSongs if song.strip()}

            for song in newSongs:
                existingSongs.add(song.lower())

            userInfo[username]['recommendedSongs'] = ';'.join(sorted(existingSongs))
        else:
            print(f"User {username} not found.")
            self.addUser(username=username, recommendedSongs=';'.join(newSongs))
            return
        self._rewrite_csv(userInfo)
        print(f"Updated recommended songs.")

    def addLikedSong(self, songTitle, artistName, username=None):
        username = username or self.username
        userInfo = self.loadingData()

        if username in userInfo:
            likedSongs = userInfo[username].get('likedSongs', '')
            likedSongsList = {song.strip().lower() for song in likedSongs.split(';') if song.strip()}
            newSong = f"{songTitle} by {artistName}".lower()

            if newSong not in likedSongsList:
                print(f"Attempting to add liked song: {songTitle} by {artistName}")
                likedSongsList.add(newSong)
                userInfo[username]['likedSongs'] = ';'.join(sorted(likedSongsList))
                self._rewrite_csv(userInfo)
            else:
                print(f"Song {songTitle} by {artistName} is already liked.")
        else:
            print(f"User {username} not found. Adding them.")
            self.addUser(
                username=username,
                likedSongs=f"{songTitle} by {artistName}"
            )