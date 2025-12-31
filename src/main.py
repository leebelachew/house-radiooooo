from cmu_graphics import *
import csv
import os
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import math
from pygame import mixer
import random
from MapGeneratorClass import MapGenerator
from ProfileClass import Profile
from spotifyUserMusicRecommenderClass import spotifyUserMusicRecommender

class Point:
    def __init__(self, x, y, city, country):
        self.x = x
        self.y = y
        self.city = city
        self.country = country

    def __repr__(self):
        return f'Point({self.x, self.y}, {self.city}, {self.country})'

    def contains(self, mouseX, mouseY):
        distance = ((mouseX - self.x) ** 2 + (mouseY - self.y) ** 2) ** 0.5
        return distance <= 4

class Label:
    def __init__(self, text, x, y, size, align, fill):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.align = align
        self.fill = fill
        self.visible = False

    def draw(self):
        if self.visible:
            drawLabel(self.text, self.x, self.y, size=self.size, align=self.align, fill=self.fill)

class Rect:
    def __init__(self, x, y, width, height, border, fill, align):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border = border
        self.fill = fill
        self.align = align

    def contains(self, mouseX, mouseY):
        return (self.x <= mouseX <= self.x + self.width and 
                self.y <= mouseY <= self.y + self.height)

class RectWithDoubleBorder:
    def __init__(self, x, y, width, height, fill, outerBorder='black', innerBorder='white', align='center'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill = fill
        self.outerBorder = outerBorder
        self.innerBorder = innerBorder
        self.align = align

    def draw(self):
        drawRect(
            self.x - 4, self.y - 4, self.width + 8, self.height + 8,
            fill=self.outerBorder, border=None
        )
        drawRect(
            self.x - 2, self.y - 2, self.width + 4, self.height + 4,
            fill=self.innerBorder, border=None
        )
        drawRect(
            self.x, self.y, self.width, self.height,
            fill=self.fill, border=None
        )
    def contains(self, mouseX, mouseY):
        return (self.x <= mouseX <= self.x + self.width and
                self.y <= mouseY <= self.y + self.height)

class Song:
    def __init__(self, title, artist, mp3File, city, decade, imageUrl=None):
        self.title = title
        self.artist = artist
        self.mp3File = mp3File
        self.city = city
        self.decade = decade
        self.imageUrl = imageUrl

def load_songs_from_csv(file_path): #Inspired by https://docs.python.org/3/library/csv.html
    songs = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            songs.append(Song(
                title=row['Title'],
                artist=row['Artist'],
                mp3File=row['File Path'],
                city=row['City'],
                decade=row['Decade'],
                imageUrl=row.get('ImageURL', None)
            ))
    return songs

def onAppStart(app):
    app.showBanner = False
    app.introMusicOn = False
    app.songs = load_songs_from_csv('absoluteimageUrls.csv')
    app.audioFeaturesCsv = "cleanedSongAudioFeatures.csv"
    app.musicMetadataCsv = "absoluteCleanedSongs.csv"
    app.mapGenerator = MapGenerator(app.audioFeaturesCsv, app.musicMetadataCsv)

    app.musicMetadata = {}
    with open(app.musicMetadataCsv, newline='', encoding='utf-8') as file: #function made using CVS extractions help inspired by 'https://www.geeksforgeeks.org/working-csv-files-python/' and ChatGPT
        userInfo = {}
        reader = csv.DictReader(file)
        for row in reader:
            title = row['Title'].strip().lower()
            app.musicMetadata[title] = {
                'artist': row['Artist'],
                'file_path': row['File Path'],
                'city': row['City'],
                'decade': row['Decade'],
            }
    app.playlist = {}
    for song in app.songs:
        city = song.city
        decade = song.decade
        if city not in app.playlist:
            app.playlist[city] = {}
        if decade not in app.playlist[city]:
            app.playlist[city][decade] = []
        app.playlist[city][decade].append(song)

    for city, decades in app.playlist.items():
        for decade, songs in decades.items():
            random.shuffle(songs)

    app.statsButton = {'x': 30, 'y': 30,'radius': 20,'color': 'blue'}

    app.buttonWidth = 150
    app.buttonHeight = 40
    app.buttonGap = 10

    app.navigationStack = []
    app.currentScreen = "home"

    app.topCity = ''
    app.topDecade = ''
    app.selectedCity = ''
    app.currentDecade = ''
    app.currentSongIndex = 0
    app.isPlaying = False
    app.user = ''
    app.typingUser = False
    app.rectWidth = 300
    app.rectHeight = 50

    app.signedIn = False
    app.signedOut = False

    app.clearScreen = False
    app.signInScreen = False
    app.showIntro = False
    app.musicPlayed = False
    app.chooseDirection = False
    app.showHouse = True
    app.whatWeRec = True
    app.whatIsHouseScreen = False

    app.loopSongPlayed = False
    app.playingLoopSong = False

    app.currentLabelIndex = 0
    app.timeCounter = 0
    app.flashCounter = 0
    app.flashEnabled = True  
    app.isSignedIn = False
    app.backgroundColor = 'white'

    app.labelSize = 24 
    app.labelGrowthRate = 6
    app.mapOn = False
    app.chooseQuiz = False

    app.playButtonGreen = Rect(375, 720, 50, 50, border= 'black', fill='green', align='center')

    buttonText = f"SIGN OUT: {app.user}"
    buttonWidth = calculateButtonWidth(buttonText)
    app.whatIsHouseButton = RectWithDoubleBorder(30, 10, app.buttonWidth, 30,
        fill='blue', align='center')
    app.shortCutButton = RectWithDoubleBorder(200, 10, 80, 30, fill = 'blue', align= 'center')
    app.signOutButton = RectWithDoubleBorder(
        app.width - app.buttonWidth - 10,
        app.whatIsHouseButton.y,
        app.buttonWidth,
        app.buttonHeight,
        fill='blue',
        align='center')
    app.heartButtonSize = 50
    app.infoButtonRadius = 20
    app.spacing = 20

    app.infoButton = {'x': app.width - app.heartButtonSize - 30, 'y': 720 + app.heartButtonSize / 2, 
        'radius': app.infoButtonRadius, 'color': 'blue'}

    app.heartButton = Rect(
            app.infoButton['x'] - app.infoButtonRadius * 2 - 50, 720,
            app.heartButtonSize, app.heartButtonSize, border='black',fill='grey', align='center')

    app.recommendationsButton = RectWithDoubleBorder(50, y=720, width=200, height=50, fill='blue')

    app.playButton = RectWithDoubleBorder((app.width - app.rectWidth) / 2, app.height / 2,
                          app.rectWidth, app.rectHeight, fill='blue', align='center')

    app.userEnter = RectWithDoubleBorder((app.width - app.rectWidth) / 2, app.height / 2,
                          app.rectWidth, app.rectHeight, fill='blue', align='center')

    app.ourRecs = RectWithDoubleBorder((app.width - app.rectWidth) / 2, app.height / 2 - 100,
        app.rectWidth, app.rectHeight, fill='blue')
    app.whatYouWant = RectWithDoubleBorder((app.width - app.rectWidth) / 2, app.height / 2,
        app.rectWidth, app.rectHeight, fill='blue')
    app.quizBox = RectWithDoubleBorder((app.width - app.rectWidth) / 2, app.height / 2,
        app.rectWidth, app.rectHeight, fill='blue')
    app.topFiveBox = RectWithDoubleBorder((app.width - app.rectWidth) / 2, app.height / 2 - 100,
        app.rectWidth, app.rectHeight, fill='blue' )

    startY = app.height / 2 - 60
    app.introLabels = [
        Label("It's about time you fell in love with something that will love you back.", app.width / 2, startY, 24, 'center', 'blue'),
        Label("And that, my friends, is house music.", app.width / 2, startY, 24, 'center', 'blue'),
        Label("It doesn't judge you, and I won't either.", app.width / 2, startY, 24, 'center', 'blue'),]
    
    app.pressed = []
    mixer.init()
    mixer.music.load("houseIntro.mp3")
    mixer.music.set_volume(0.7)
    app.showCoverImage = False
    app.url = '/Users/leyubelachew/Desktop/Turnin/src/thankYouElaine.png'

    app.decadeLabels = ["1980s", "1990s", "2000s", "2010s"]
    app.boxWidth = 90
    app.boxHeight = 20
    app.whiteBoxMargin = 10

    app.houseX = -400
    app.houseY = 100
    app.houseSpeed = 10

    app.bannerX = -300
    app.bannerY = 100
    app.bannerSpeed = 10

    app.cityPositions = {
        "USA": [
            Point(140, 290, "Chicago", "USA"),
            Point(160, 280, "Detroit", "USA"),
            Point(170, 291, "New York", "USA"),
            Point(50, 325, "Los Angeles", "USA")
        ],
        "Germany": [Point(375, 290, "Berlin", "Germany")],
        "France": [Point(355, 295, "Paris", "France")],
        "UK": [Point(335, 289, "London", "UK")],
        "Spain": [
            Point(340, 322, "Ibiza", "Spain"),
            Point(340, 310, "Barcelona", "Spain")
        ],
        "Netherlands": [Point(350, 280, "Amsterdam", "Netherlands")],
        "Sweden": [Point(370, 265, "Stockholm", "Sweden")],
        "Brazil": [Point(225, 485, "Rio", "Brazil")],
        "Colombia": [Point(150, 420, "Bogota", "Colombia")],
        "Nigeria": [Point(340, 410, "Lagos", "Nigeria")],
        "South Africa": [
            Point(375, 518, "Cape Town", "South Africa"),
            Point(395, 500, "Johannesburg", "South Africa")
        ]
    }

    app.pointPressed = None
    app.year = ''
    app.song = ''
    app.skipButton = Rect(440, 720, 50, 50, border= None, fill='blue', align='center')
    app.backButton = Rect(310, 720, 50, 50, border= None, fill='blue', align='center')

    app.currentDecade = ''
    app.selectedCity = ''
    app.artist = ''
    app.currentSongIndex = 0
    app.isPlaying = False

    app.audioFeaturesCsv = "cleanedSongAudioFeatures.csv"
    app.musicMetadataCsv = "absoluteCleanedSongs.csv"

    app.byQuiz = False
    app.byTopFive = False
    app.userTopTrackFeatures = None

    app.quizQuestions = ['Popularity','Energy','Danceability','Positiveness','Speechiness',
                       'Liveness','Acousticness','Instrumentalness','Tempo']

    app.indexOfQuestion = 0
    app.currentInput = ''
    app.quizComplete = False
    app.quizRecommender = None
    app.userAnswers = []
    app.quizRecommendations = []
    
    app.pastVectors = []
    app.recommendedSongs = []
    app.likedSongs = []
    app.showStatsPage = False
    app.showQuizRecommendations = False

    app.importButton = RectWithDoubleBorder((app.width - 150) / 2, app.height - 100, 150, 50, fill='blue', align='center')
    
    app.mapImage = None
    app.showStatsPage = False
    app.whatIsHouseLines = [
        "House music isn’t just sound—it’s a feeling.",
        "It’s the joy, the freedom, and the connection you feel when",
        "the beat takes over. Born in Chicago clubs like the Warehouse,",
        "it gave people a space to be themselves,",
        "to dance, and to let go.",
        "It’s more than music; it’s an experience.",
        "It’s that moment when a song gives you chills or when a crowd",
        "moves as one, lost in the rhythm. House music brings people",
        "together, making everyone feel alive and free.",
        "From its start with legends like Frankie Knuckles to its",
        "spread around the world, house is all about energy, emotion,",
        "and community. Whether you’re in a tiny club or a huge festival,",
        "house music is a reminder: dance, feel, and just be yourself."
    ]
    
    app.shortCutScreen = False
    app.likedSongsSC = ['Press covers to listen', 'Press "m" to go to map']
    app.onRecSC = ['Press "m" to go to map']
    app.onMapSC = ['Press "m" to go to current listening']
    app.onAlbumSC = ['Press "m" to go to map']
    app.onStatsSC = ['Press "c" to clear history', 'Press "m" to go to map']
    app.onShortCutSC = ['Press "m" to go to map']
    app.stateLines = {'On Liked Tracks': app.likedSongsSC, 
                      'On Recommendations': app.onRecSC, 'On Map': app.onMapSC, 
                      'On Current Listening': app.onAlbumSC, 'On Stats': app.onStatsSC, 
                      'On ShortCuts': app.onShortCutSC}

def redrawAll(app):
    if app.introMusicOn:
        drawRect(0, 0, app.width, app.height, fill=app.backgroundColor)
    if app.showIntro:
        for label in app.introLabels:
            if label.visible:
                drawLabel(label.text, label.x, label.y, size=label.size, align=label.align, fill=label.fill, font = 'Orbitron')
    else:
        drawRect(0, 0, app.width, app.height, fill=app.backgroundColor)

    if app.signInScreen and app.signedOut:
        frameWidth, frameHeight = 800, 800

        drawImage('SignOut.png', -8, 0, width=frameWidth, height=frameHeight)
        drawLabel('Press Enter to Sign In', app.width / 2, app.height / 2 + 40, 
                  size=18, align='center', fill='black', font='Orbitron')
        
    if app.signedIn:
        drawCircle( app.infoButton['x'], app.infoButton['y'], app.infoButton['radius'],
        fill=app.infoButton['color'], border='white')
        drawLabel('i', app.infoButton['x'], app.infoButton['y'], size=20,bold=True,
            align='center',fill='white', font = 'Orbitron')

        buttonText = f"SIGN OUT: {app.user}"
        buttonWidth = calculateButtonWidth(buttonText)
        app.signOutButton.width = buttonWidth
        app.signOutButton.x = app.width - buttonWidth - 30
        
        drawRect(app.signOutButton.x, app.signOutButton.y, 
                app.signOutButton.width, app.signOutButton.height,
                fill='white', border='black')
        
        blueBoxMargin = 4
        blueBoxX = app.signOutButton.x + blueBoxMargin
        blueBoxY = app.signOutButton.y + blueBoxMargin
        blueBoxWidth = app.signOutButton.width - 2 * blueBoxMargin
        blueBoxHeight = app.signOutButton.height - 2 * blueBoxMargin

        drawRect(blueBoxX, blueBoxY, blueBoxWidth, blueBoxHeight,
                fill=app.signOutButton.fill, border=None)
        
        drawLabel(buttonText, 
                app.signOutButton.x + app.signOutButton.width / 2, 
                app.signOutButton.y + app.signOutButton.height / 2, 
                size=14, bold=True, align='center', fill='white', font = 'Orbitron')
        
        if app.shortCutScreen == False:
            app.shortCutButton.draw()
            drawLabel("ShortCuts",app.shortCutButton.x + app.shortCutButton.width / 2,app.shortCutButton.y + app.shortCutButton.height / 2,
                size=14,bold=True, align='center',fill='white', font = 'Orbitron')
        if app.shortCutScreen:
            drawLabel("Shortcuts", app.width / 2, 50, fill='white', font='Orbitron', size=35, bold=True)
            y = 135
            for state, shortcuts in app.stateLines.items():
                drawLabel(state, app.width / 2, y, fill='white', size=25, bold=True, font = 'Orbitron')
                y += 30
                for shortcut in shortcuts:
                    drawLabel(shortcut, app.width / 2, y, fill='white', size=20, font = 'Orbitron')
                    y += 25
                y += 20 

        if app.whatIsHouseScreen == False:
            app.whatIsHouseButton.draw()
            drawLabel(
                "WHAT IS HOUSE?", app.whatIsHouseButton.x + app.whatIsHouseButton.width / 2,
                app.whatIsHouseButton.y + app.whatIsHouseButton.height / 2, size=14, bold=True,align='center',
                fill='white', font = 'Orbitron')
            
    if app.whatIsHouseScreen:
        drawLabel('WHAT IS HOUSE?', app.width / 2, 90, fill = 'white', font= 'Orbitron', size = 35, bold = True)
        totalHeight = len(app.whatIsHouseLines) * 20
        startY = (app.height - totalHeight) // 2 - 35

        for i in range(len(app.whatIsHouseLines)):
            line = app.whatIsHouseLines[i]
            drawLabel(line, app.width // 2, startY + i * 20, align='center', fill='white', size=20, font='Orbitron')

    if app.clearScreen:
        return
    
    if app.backgroundColor == 'blue' and app.showHouse == True:
        drawLabel('HOUSE RADIOOOOO', app.width / 2, app.height / 2,
                  size=app.labelSize, align='center', fill='white', font = 'Orbitron', bold = True)
        drawLabel('Press Enter', app.width / 2, app.height / 2 + 50, size = 16, fill = 'white', font = 'Orbitron')

    if app.signInScreen:
        app.userEnter.draw()
        if not app.user:
            drawLabel('username', app.userEnter.x + 10, app.userEnter.y + app.userEnter.height / 2,
                      size=20, align='left', fill='white', font = 'Orbitron')

        drawLabel(app.user, app.userEnter.x + 10, app.userEnter.y + app.userEnter.height / 2,
                  size=20, align='left', fill='white', font = 'Orbitron')
        return

    if app.chooseDirection:
        if app.ourRecs:
            app.ourRecs.draw()
            drawLabel('What We Recommend', app.ourRecs.x + app.ourRecs.width / 2, app.ourRecs.y + app.ourRecs.height / 2,
                      size=20, align='center', fill='white', font = 'Orbitron')
            
        if app.whatYouWant:
            app.whatYouWant.draw()
            drawLabel('What You Want', app.whatYouWant.x + app.whatYouWant.width / 2, app.whatYouWant.y + app.whatYouWant.height / 2,
                      size=20, align='center', fill='white', font = 'Orbitron')

    if app.chooseQuiz:
        drawLabel('Types Of Recommendation', app.width//2, app.height//2 - 150, size =30, bold=True, fill='white', font = 'Orbitron')
        app.quizBox.draw()
        drawLabel('Quiz', app.quizBox.x + app.quizBox.width / 2, app.quizBox.y + app.quizBox.height / 2,
                      size=20, align='center', fill='white', font = 'Orbitron')
        
        app.topFiveBox.draw()
        drawLabel('Your Liked Tracks', app.topFiveBox.x + app.topFiveBox.width / 2, app.topFiveBox.y + app.topFiveBox.height / 2,
                      size=20, align='center', fill='white', font = 'Orbitron')

    if app.byTopFive:
        drawLabel(f"{app.user}'s Liked Tracks", app.width / 2, 85, size=24, align='center', fill='white', bold=True, font = 'Orbitron')
        yStart = 120
        xCover = 50
        xText = 200
        spacing = 120

        for i in range(len(app.likedSongs)):
            song = app.likedSongs[i]
            coverUrl = song.get('cover')
            title = song.get('title', 'Unknown Title')
            artist = song.get('artist', 'Unknown Artist')

            coverTopLeftX = xCover
            coverTopLeftY = yStart + i * spacing
            drawRect(coverTopLeftX - 5, coverTopLeftY - 5, 110, 110, fill='white', border=None)

            if coverUrl:
                drawImage(coverUrl, coverTopLeftX, coverTopLeftY, width=100, height=100)
            else:
                drawLabel("[No Cover]", coverTopLeftX + 50, coverTopLeftY + 50, size=12, align='center', fill='gray', font = 'Orbitron')

            drawLabel(f"{i + 1}. {title.title()} by {artist}", xText, yStart + i * spacing + 50, size=18, align='left', fill='white', font = 'Orbitron')


    if app.chooseQuiz == False and app.byQuiz == True and app.quizComplete == False:
        if app.indexOfQuestion < len(app.quizQuestions):
            drawLabel(f'On a scale of 1 to 10, how much do you like {app.quizQuestions[app.indexOfQuestion]}?',
                    app.width // 2, app.height // 2 - 100, fill='white', size=23, font = "Orbitron")
            drawLabel(f'Your Current Input: {app.currentInput}', app.width // 2, app.height // 2 - 60, size=20, fill='white', font = 'Orbitron')
        
        profile = Profile(app.user)
        userData = profile.loadingData().get(app.user, {})
        pastAnswers = userData.get('pastAnswers', '')

        if pastAnswers:
            pastAnswersMatrix = [list(map(float, vec.split(','))) for vec in pastAnswers.split('|')]
        else:
            pastAnswersMatrix = []

        combinedAnswersMatrix = pastAnswersMatrix + [app.userAnswers]
        drawLabel('Your Personal Vector:', app.width // 2, app.height // 2, size=20, fill='white', font = 'Orbitron')

        matrixYStart = app.height // 2 + 40  # Starting Y position
        lineSpacing = 30

        for rowIndex in range(len(combinedAnswersMatrix)):
            row = combinedAnswersMatrix[rowIndex]
            rowText = '[' + ', '.join(f'{value:.2f}' for value in row) + ']' #Use of .2f inspired by https://www.freecodecamp.org/news/2f-in-python-what-does-it-mean/

            y = matrixYStart + rowIndex * lineSpacing
            drawLabel(rowText, app.width // 2, y, size=20, fill='white', align='center', font = 'Orbitron')


        drawLabel('Press Enter to submit, Backspace to revise.', 
                app.width // 2, matrixYStart + len(combinedAnswersMatrix) * lineSpacing + 30, size=18, fill='white', font = 'Orbitron')
    if app.quizComplete and app.showQuizRecommendations:
        drawLabel(f"Top City: {app.topCity}", app.width / 2, 70, size=20, bold=True, align="center", fill="white", font = 'Orbitron')
        drawLabel(f"Top Decade: {app.topDecade}", app.width / 2, 100, size=20, bold=True, align="center", fill="white", font = 'Orbitron')

        cols = 5
        rows = 2
        albumWidth = 80
        albumHeight = 80
        spacingX = 160
        spacingY = 180
        totalAlbumWidth = (cols - 1) * spacingX + albumWidth
        totalAlbumHeight = (rows - 1) * spacingY + albumHeight
        startX = (app.width - totalAlbumWidth) / 2
        startY = (app.height - totalAlbumHeight) / 2

        for i in range(len(app.quizRecommendations[:cols * rows])):
            songName, songData = app.quizRecommendations[i]
            col = i % cols
            row = i // cols
            x = startX + col * spacingX
            y = startY + row * spacingY

            drawRect(x - 5, y - 5, albumWidth + 10, albumHeight + 10, fill="white", border=None)
            coverUrl = songData.get("imageUrl", None)

            if coverUrl:
                drawImage(coverUrl, x, y, width=albumWidth, height=albumHeight)
            else:
                drawLabel("[No Cover]", x + albumWidth / 2, y + albumHeight / 2, size=12, align="center", fill="gray", font = 'Orbitron')

            drawLabel(songName, x + albumWidth / 2, y + albumHeight + 15, size=10, align="center", fill="white", bold=True, font = 'Orbitron')
            drawLabel(f"by {songData['artist']}", x + albumWidth / 2, y + albumHeight + 35, size=9, align="center", fill="lightgray", font = 'Orbitron')
            drawLabel(f"Score: {songData['score']:.1f}%", x + albumWidth / 2, y + albumHeight + 50, size=9, align="center", fill="black", font = 'Orbitron')
            drawLabel(f"{songData['city']}, {songData['decade']}", x + albumWidth / 2, y + albumHeight + 65, size=9, align="center", fill="lightblue", font = 'Orbitron')
            if app.importButton:
                app.importButton.draw()
                drawLabel("Import to Spotify", app.importButton.x + app.importButton.width / 2,
                        app.importButton.y + app.importButton.height / 2, size=16, align="center", fill="white", font = 'Orbitron')
    
    if app.playButton:
        app.playButton.draw()
        drawLabel('Play', app.playButton.x + app.playButton.width / 2, app.playButton.y + app.playButton.height / 2,
                  size=20, align='center', fill='white', font = 'Orbitron')

    if app.mapOn:
        imageWidth, imageHeight = getImageSize(app.url)
        windowWidth, windowHeight = 800, 800
        scaleX = windowWidth / imageWidth
        scaleY = windowHeight / imageHeight
        
        scaleFactor = min(scaleX, scaleY)
        scaledWidth = imageWidth * scaleFactor
        scaledHeight = imageHeight * scaleFactor
        
        drawImage(app.url, windowWidth // 2, windowHeight // 2, 
                width=scaledWidth, height=scaledHeight, align='center')
        drawLabel('HOUSE RADIOOOOO', app.houseX, app.houseY, size = 60, fill = 'white', font = 'Orbitron', bold = True, align = 'center')
        
        for country, cities in app.cityPositions.items():
            for city in cities:
                drawCircle(city.x, city.y, 4, fill='red')

        totalSpacing = app.width - (app.boxWidth * len(app.decadeLabels))
        spaceBetweenBoxes = totalSpacing // (len(app.decadeLabels) + 1)

        for i in range(len(app.decadeLabels)):
            boxX = (i + 1) * spaceBetweenBoxes + i * app.boxWidth
            
            boxY = 650
            drawRect(boxX - app.whiteBoxMargin, boxY - app.whiteBoxMargin,
                    app.boxWidth + app.whiteBoxMargin * 2, app.boxHeight + app.whiteBoxMargin * 2,
                    fill='white', border='black')
            
            drawRect(boxX, boxY, app.boxWidth, app.boxHeight, fill='blue', border=None)
            labelX = boxX + app.boxWidth / 2
            labelY = boxY + app.boxHeight / 2
            drawLabel(app.decadeLabels[i], labelX, labelY, size=16, bold=True, fill='white', align='center')

        drawRect(app.playButtonGreen.x, app.playButtonGreen.y, 
                app.playButtonGreen.width, app.playButtonGreen.height, 
                fill=app.playButtonGreen.fill, border=app.playButtonGreen.border)
        drawLabel('Play' if not app.isPlaying else 'Pause', 
                app.playButtonGreen.x + app.playButtonGreen.width // 2, 
                app.playButtonGreen.y + app.playButtonGreen.height // 2, 
                align='center', size=12, fill='white')

        drawRect(app.backButton.x, app.backButton.y, 
                app.backButton.width, app.backButton.height, 
                fill=app.backButton.fill, border=app.backButton.border)
        drawLabel('<', app.backButton.x + app.backButton.width // 2, 
                app.backButton.y + app.backButton.height // 2, 
                align='center', size=20, fill='white')

        drawRect(app.skipButton.x, app.skipButton.y, 
                app.skipButton.width, app.skipButton.height, 
                fill=app.skipButton.fill, border=app.skipButton.border)
        drawLabel('>', app.skipButton.x + app.skipButton.width // 2, 
                app.skipButton.y + app.skipButton.height // 2, 
                align='center', size=20, fill='white')
        
        drawRect(app.heartButton.x, app.heartButton.y, app.heartButton.width, app.heartButton.height,
            fill=app.heartButton.fill,border=app.heartButton.border)
        drawLabel("♥", app.heartButton.x + app.heartButton.width / 2, app.heartButton.y + app.heartButton.height / 2,
            size=20, bold=True, align='center', fill='white')
        app.recommendationsButton.draw()
        drawLabel('Recommendations', app.recommendationsButton.x + app.recommendationsButton.width / 2,
                app.recommendationsButton.y + app.recommendationsButton.height / 2, size=16, bold=True, fill='white', 
                align='center', font = 'Orbitron')


    if app.showCoverImage and app.currentCoverUrl:
        rectWidth = 340
        rectHeight = 340
        centerX = app.width / 2
        centerY = app.height / 2

        drawRect( centerX - rectWidth / 2, centerY - rectHeight / 2, rectWidth, rectHeight, fill="white", border=None)
        drawImage(app.currentCoverUrl, app.width / 2 - 150, app.height / 2 - 150, width=300, height=300)
        drawLabel(f'{app.song.title} by {app.song.artist} playing in {app.selectedCity}, {app.year}', app.width//2, app.height//2 + 200, fill = 'white', size = 16, font = 'Orbitron' )
        drawLabel(f'Your listening to {app.song.title} by {app.song.artist} On HOUSE RADIOOOOO', app.bannerX, app.bannerY, size = 35, fill = 'white', font = 'Orbitron', bold = True, align = 'center')
        drawRect(app.playButtonGreen.x, app.playButtonGreen.y, app.playButtonGreen.width, app.playButtonGreen.height, 
                fill=app.playButtonGreen.fill, border=app.playButtonGreen.border)
        drawLabel('Play' if not app.isPlaying else 'Pause', app.playButtonGreen.x + app.playButtonGreen.width // 2, app.playButtonGreen.y + app.playButtonGreen.height // 2, 
                align='center', size=12, fill='white')

        drawRect(app.backButton.x, app.backButton.y, app.backButton.width, app.backButton.height, fill=app.backButton.fill, border=app.backButton.border)
        drawLabel('<', app.backButton.x + app.backButton.width // 2, app.backButton.y + app.backButton.height // 2, align='center', size=20, fill='white')

        drawRect(app.skipButton.x, app.skipButton.y, app.skipButton.width, app.skipButton.height, fill=app.skipButton.fill, border=app.skipButton.border)
        drawLabel('>', app.skipButton.x + app.skipButton.width // 2, app.skipButton.y + app.skipButton.height // 2, align='center', size=20, fill='white')
        
        drawRect(app.heartButton.x, app.heartButton.y,app.heartButton.width,
            app.heartButton.height, fill=app.heartButton.fill, border=app.heartButton.border)
        drawLabel( "♥", app.heartButton.x + app.heartButton.width / 2, app.heartButton.y + app.heartButton.height / 2,
            size=20, bold=True, align='center', fill='white')
        app.recommendationsButton.draw()
        drawLabel('Recommendations', app.recommendationsButton.x + app.recommendationsButton.width / 2, app.recommendationsButton.y + app.recommendationsButton.height / 2,
                size=16, bold=True, fill='white', align='center', font = 'Orbitron')
    
    if app.showStatsPage:
        profile = Profile(app.user)
        userData = profile.loadingData().get(app.user, {})
        likedSongs = userData.get('likedSongs', '').split(';')
        recommendedSongs = userData.get('recommendedSongs', '').split(';')

        drawLabel(f"{app.user}'s Statistics", app.width / 2, 65, size=30, bold=True, fill='white', font = 'Orbitron')
        drawLabel(f"Username: {app.user}", app.width / 2, 100, size=20, fill='white', font = 'Orbitron')
        drawLabel(f"Liked Songs: {len([s for s in likedSongs if s])}", app.width / 2, 130, size=18, fill='white', font = 'Orbitron')
        drawLabel(f"Recommended Songs: {len([s for s in recommendedSongs if s])}", app.width / 2, 160, size=18, fill='white', font = 'Orbitron')

        rectWidth = 700
        rectHeight = 330
        rectX = (app.width - rectWidth) // 2
        rectY = (app.height - rectHeight) // 2 - 45
        drawRect(rectX, rectY, rectWidth, rectHeight, fill='white')

        if app.mapImage:
            mapX = app.width / 2
            mapY = rectY + rectHeight / 2 + 20
            drawImage(app.mapImage, mapX, mapY, align='center')

        profile = Profile(app.user)
        userData = profile.loadingData().get(app.user, {})
        pastAnswers = userData.get("pastAnswers", "")
        pastVectors = [list(map(float, vec.split(','))) for vec in pastAnswers.split('|') if vec]

        drawLabel("Your Past Answer Vectors:", app.width / 2, rectY + rectHeight + 40, size=20, fill='white', bold=True, font = 'Orbitron')

        matrixStartY = rectY + rectHeight + 70
        lineSpacing = 20

        for i in range(len(pastVectors)):
            vector = pastVectors[i]
            vectorStr = "[" + ", ".join(f"{v:.2f}" for v in vector) + "]" # Use of .2f inspired by https://www.freecodecamp.org/news/2f-in-python-what-does-it-mean/
            drawLabel(vectorStr, app.width / 2, matrixStartY + i * lineSpacing, size=20, fill='white', align='center', font = 'Orbitron')
def clearCanvas(app):
    app.clearScreen = True

def onKeyPress(app, key):
    if key == "enter" and app.showIntro:
        navigateToScreen(app, "signInScreen")

    if app.signInScreen and app.typingUser:
        if key == 'enter' and app.user:
            app.introMusicOn = False
            app.isSignedIn = True
            app.signedIn = True
            app.signedOut = False
            app.quizRecommender = None
            app.clearScreen = False
            app.showIntro = False
            app.signInScreen = False
            app.chooseDirection = True
            app.showHouse = False
            app.backgroundColor = 'blue'
            app.shortCutScreen = False
            app.whatIsHouseScreen = False

        elif key == 'backspace':
            app.user = app.user[:-1] if app.user else ''
        elif key.isalpha() or key.isdigit() or key == '-':
            app.user += key

    elif app.showIntro and key == "enter":
        app.showIntro = False
        app.signInScreen = True
        app.backgroundColor = 'blue'
        mixer.music.stop()

    if app.byQuiz:
        if key == 'backspace':
            if app.currentInput:
                app.currentInput = app.currentInput[:-1]
            elif app.indexOfQuestion > 0 and app.userAnswers:
                app.indexOfQuestion -= 1
                app.currentInput = str(int(app.userAnswers.pop() * 10))
                
        elif key == 'enter':
            try:
                answer = int(app.currentInput)
                if 1 <= answer <= 10:
                    normalizedAnswer = answer / 10
                    app.userAnswers.append(normalizedAnswer)
                    app.currentInput = ''
                    app.indexOfQuestion += 1
                    if app.indexOfQuestion >= len(app.quizQuestions):
                        app.quizComplete = True
                        quizRecommendations(app)
                else:
                    app.currentInput = "Enter a number between 1 and 10."
            except ValueError:
                app.currentInput = "Invalid input!"

        elif key.isdigit():
            app.currentInput += key
            
    if key == 'm':
        if app.showStatsPage == True or app.quizComplete == True or app.shortCutScreen == True or app.whatIsHouseScreen == True or app.byTopFive == True:
            app.mapOn = True
            app.showStatsPage = False
            app.quizComplete = False
            app.showQuizRecommendations = False
            app.chooseQuiz = False
            app.byQuiz = False
            app.showHouse = False
            app.chooseDirection = False
            app.signInScreen = False
            app.whatIsHouseScreen = False
            app.shortCutScreen = False
            app.byTopFive = False
            print(app.background)

        if app.mapOn:
            app.showStatsPage = False
            app.quizComplete = False
            app.showQuizRecommendations = False
            app.chooseQuiz = False
            app.byQuiz = False
            app.byTopFive = False
            app.showHouse = False
            app.chooseDirection = False
            app.signInScreen = False
            app.whatIsHouseScreen = False
            app.background = 'blue'
            app.shortCutScreen = False

            if app.song:
                app.showBanner = True
                app.currentCoverUrl = getCoverImage(spotify_client, app.song.title, app.song.artist)
                
                if app.currentCoverUrl:
                    print(f"Cover image URL: {app.currentCoverUrl}")
                    app.showCoverImage = True
                    app.mapOn = False
                else:
                    app.showCoverImage = False
                    app.mapOn = True
        elif app.showCoverImage:
            app.showBanner = False
            app.showCoverImage = False
            app.mapOn = True
            app.whatIsHouseScreen = False
            app.shortCutScreen = False
            app.showStatsPage = False

    if app.showStatsPage:
        if key == 'c':
            clearUserStats(app)
            app.statsClearMessage = "Stats cleared"

def quizRecommendations(app):
    if not app.quizRecommender:
        app.quizRecommender = spotifyUserMusicRecommender( app.user, app.audioFeaturesCsv, app.musicMetadataCsv, spotify_client)
    userVector = [answer / 10 for answer in app.userAnswers]
    if not isinstance(userVector, list):
        raise TypeError("userVector must be a list.") #Debug inspired by CHATGPT

    app.quizRecommendations = app.quizRecommender.getTopCompatibleSongs([userVector], userVector, 10)
    for songName, metadata in app.quizRecommendations:
        metadata["imageUrl"] = getCoverImage(spotify_client, songName, metadata["artist"])
    print(app.quizRecommendations)

    profile = Profile(app.user)
    profile.updatePastAnswers(newVector=userVector, username=app.user)

    app.showQuizRecommendations = True

    mostCompatibleDecade, mostCompatibleCity, mostCompatibleCityAndDecade = app.quizRecommender.findMostCompatibleCityDecade(app.quizRecommendations)
    app.topCity = mostCompatibleCity
    app.topDecade = mostCompatibleDecade

def onStep(app):
    if app.showIntro:
        app.timeCounter += 1

        if not app.isSignedIn and app.playingLoopSong:
            app.flashCounter += 1
            if app.flashCounter % 30 == 0:
                app.backgroundColor = 'blue' if app.backgroundColor == 'white' else 'white'
                if app.backgroundColor == 'blue':
                    app.labelSize += app.labelGrowthRate
        else:
            app.backgroundColor = 'blue'

        if app.timeCounter % 90 == 0:
            for label in app.introLabels:
                label.visible = False

            app.currentLabelIndex = (app.currentLabelIndex + 1) % len(app.introLabels)
            app.introLabels[app.currentLabelIndex].visible = True

            if app.currentLabelIndex == len(app.introLabels) - 1:
                if not mixer.music.get_busy():
                    app.enterRect.visible = True

        if not app.playingLoopSong and not mixer.music.get_busy():
            mixer.music.load("allThatJunk.mp3")
            mixer.music.play(-1)
            app.introMusicOn = True
            app.playingLoopSong = True

    if app.mapOn:
        app.houseX += app.houseSpeed
        if app.houseX - 300 > 800:
            app.houseX = -300

        if app.isPlaying and not mixer.music.get_busy():
            if app.selectedCity and app.currentDecade:
                print("Song finished. Moving to the next track...")
                skipToNextTrack(app)
            else:
                print("Cannot skip track: No city or decade selected.")

    if app.showCoverImage:
        app.bannerX += app.houseSpeed

        text = f"Your listening to {app.song.title} by {app.song.artist} On HOUSE RADIOOOOO"
        bannerWidth = len(text) * 20

        if app.bannerX > app.width + bannerWidth:
            app.bannerX = -bannerWidth 

def clearUserStats(app):
    profile = Profile(app.user)
    userInfo = profile.loadingData()

    if app.user in userInfo:
        userInfo[app.user]['recommendedSongs'] = ''
        userInfo[app.user]['likedSongs'] = ''
        profile._rewrite_csv(userInfo)  # Rewrite the CSV file, inspired by 'https://www.geeksforgeeks.org/working-csv-files-python/'
        print(f"Cleared stats for user: {app.user}")
    else:
        print(f"User {app.user} not found.")

def onMousePress(app, mouseX, mouseY):
    app.mouseX = mouseX
    app.mouseY = mouseY

    if 70 <= mouseX <= 170 and 70 <= mouseY <= 110:
        if app.navigationStack:
            app.currentScreen = app.navigationStack.pop()
        return

    if app.signInScreen:
        navigateToScreen(app, "signIn")
    elif app.chooseDirection:
        if app.ourRecs.contains(mouseX, mouseY):
            navigateToScreen(app, "quizScreen")
        elif app.whatYouWant.contains(mouseX, mouseY):
            navigateToScreen(app, "mapScreen")

    if app.signedIn:
        if (app.signOutButton.x <= mouseX <= app.signOutButton.x + app.signOutButton.width and
        app.signOutButton.y <= mouseY <= app.signOutButton.y + app.signOutButton.height):
            app.signedOut = True
            if mixer.music.get_busy():
                mixer.music.stop()
            app.user = ''
            app.typingUser = False
            app.signInScreen = True
            app.chooseDirection = False
            app.whatIsHouseScreen = False
            app.showStatsPage = False
            app.showCoverImage = False
            app.shortCutScreen = False

    if app.whatIsHouseButton.contains(mouseX, mouseY):
        app.whatIsHouseScreen = True
        app.showStatsPage = False
        app.signInScreen = False
        app.chooseDirection = False
        app.chooseQuiz = False
        app.byQuiz = False
        app.byTopFive = False
        app.showCoverImage = False
        app.shortCutScreen = False
        app.mapOn = False
        print("What is House button clicked!")
        
    if app.shortCutButton.contains(mouseX, mouseY):
        app.mapOn = False
        app.chooseDirection = False
        app.chooseQuiz = False
        app.byTopFive = False
        app.byQuiz = False
        app.showStatsPage = False
        app.whatIsHouseScreen = False
        app.showCoverImage = False
        app.shortCutScreen = True
        
    if ((mouseX - app.infoButton['x'])**2 + (mouseY - app.infoButton['y'])**2 <= app.infoButton['radius']**2):
        app.background = 'blue'
        app.byTopFive = False
        app.quizComplete= False
        app.showQuizRecommendations = False
        app.chooseQuiz = False
        app.byQuiz = False
        app.mapOn = False
        app.whatIsHouseScreen = False
        app.showStatsPage = True
        app.showCoverImage = False
        app.shortCutScreen = False

        generate_map_for_user(app)
        if app.showStatsPage:
            if 70 <= mouseX <= 170 and 70 <= mouseY <= 110:
                app.showStatsPage = False

    if app.heartButton.contains(mouseX, mouseY):
        if app.song:
            profile = Profile(app.user)
            userData = profile.loadingData().get(app.user, {})
            likedSongs = userData.get("likedSongs", "").split(";")
            currentSong = f"{app.song.title} by {app.song.artist}".strip().lower()

            if currentSong in [song.strip().lower() for song in likedSongs]:
                likedSongs = [song for song in likedSongs if song.strip().lower() != currentSong]
                userData["likedSongs"] = ";".join(likedSongs)
                profile._rewrite_csv({app.user: userData})
                print(f"Unliked song: {app.song.title}")
                app.heartButton.fill = 'grey'
            else:
                profile.addLikedSong(app.song.title, app.song.artist, username=app.user)
                app.heartButton.fill = 'red'
                print(f"Liked song: {app.song.title}")
        else:
            print("No song playing.")

    if app.playButton and app.playButton.contains(mouseX, mouseY):
        app.playButton = None
        app.showIntro = True
        app.introLabels[0].visible = True
        mixer.music.play()
        app.musicPlayed = True

    if app.signInScreen and app.userEnter.contains(mouseX, mouseY):
        app.typingUser = True

    if app.chooseDirection:
        if app.ourRecs.contains(mouseX, mouseY):
            app.chooseDirection = False
            app.chooseQuiz = True

        elif app.whatYouWant.contains(mouseX, mouseY):
            app.chooseDirection = False
            app.mapOn = True
        app.backgroundColor = 'blue'
        return

    if app.chooseQuiz:
        if app.quizBox.contains(mouseX, mouseY):
            app.chooseQuiz = False
            app.byQuiz = True
            app.backgroundColor = 'blue'

        if app.topFiveBox.contains(mouseX, mouseY):
            print("Liked Songs Box pressed")
            app.chooseQuiz = False
            app.byTopFive = True
            fetchLikedSongs(app, spotify_client)
            app.backgroundColor = 'blue'

    if app.importButton.contains(mouseX, mouseY) and app.quizComplete:
        importSongs(app)

    if app.mapOn:
        app.quizComplete = False
        app.showQuizRecommendations = False
        app.chooseQuiz = False
        app.byQuiz = False
        app.byTopFive = False
        app.showStatsPage = False
        app.shortCutScreen = False
        app.whatIsHouseScreen = False
        app.showCoverImage = False

        for country, cities in app.cityPositions.items():
            for city in cities:
                if city.contains(mouseX, mouseY):
                    if app.isPlaying:
                        mixer.music.stop()
                        app.isPlaying = False
                        app.playButtonGreen.fill = 'green'

                    app.selectedCity = city.city
                    print(f"City pressed: {app.selectedCity}")

                    app.currentDecade = ''
                    app.currentSongIndex = 0

                    if app.selectedCity in app.playlist:
                        app.decadeLabels = list(app.playlist[app.selectedCity].keys())
                    else:
                        app.decadeLabels = []
                    break

        totalSpacing = app.width - (app.boxWidth * len(app.decadeLabels))
        spaceBetweenBoxes = totalSpacing // (len(app.decadeLabels) + 1)

        for i in range(len(app.decadeLabels)):
            boxX = (i + 1) * spaceBetweenBoxes + i * app.boxWidth
            boxY = 650

            if boxX <= mouseX <= boxX + app.boxWidth and boxY <= mouseY <= boxY + app.boxHeight:
                setCityAndDecade(app, app.selectedCity, app.decadeLabels[i])
                print(f"Decade pressed: {app.decadeLabels[i]}")

                if app.selectedCity in app.playlist:
                    selectedSongs = app.playlist[app.selectedCity][app.currentDecade]
                    if selectedSongs:
                        random.shuffle(selectedSongs)
                        selectedSong = selectedSongs[0]
                        app.song = selectedSong
                        mixer.music.load(selectedSong.mp3File)
                        mixer.music.play()
                        app.isPlaying = True
                        app.playButtonGreen.fill = 'red'
                        print(f"Now playing: {selectedSong.title} by {selectedSong.artist}")
                break
        
        if app.playButtonGreen.contains(mouseX, mouseY):
            if app.isPlaying:
                mixer.music.pause()
                app.isPlaying = False
                app.playButtonGreen.fill = 'green'
                print("Song paused.")
            else:
                mixer.music.unpause()
                app.isPlaying = True
                app.playButtonGreen.fill = 'red'
                print("Song resumed.")

        elif app.skipButton.contains(mouseX, mouseY):
            skipToNextTrack(app)

        elif app.backButton.contains(mouseX, mouseY):
            skipToPreviousTrack(app)

        if app.recommendationsButton.contains(mouseX, mouseY):
            app.mapOn = False
            app.chooseDirection = False
            app.chooseQuiz = True
            app.byTopFive = False
            app.byQuiz = False
            app.showStatsPage = False
            app.whatIsHouseScreen = False
            app.shortCutScreen = False

    if app.byTopFive:
        yStart = 100
        xCover = 50
        spacing = 120

        for i in range(len(app.likedSongs)):
            song = app.likedSongs[i]
            coverTopLeftX = xCover
            coverTopLeftY = yStart + i * spacing
            coverBottomRightX = coverTopLeftX + 100
            coverBottomRightY = coverTopLeftY + 100

            if (coverTopLeftX <= mouseX <= coverBottomRightX and
                coverTopLeftY <= mouseY <= coverBottomRightY):
                
                app.song = song
                mixer.music.load(song['file_path'])
                mixer.music.play()
                app.isPlaying = True
                app.playButtonGreen.fill = 'red'


                app.currentCity = song.get('city', 'Unknown City')
                app.currentDecade = song.get('decade', 'Unknown Decade')
                print(f"Playing: {song['title']} by {song['artist']}")
                break

    if app.showQuizRecommendations and app.quizRecommendations:
        startX = 50
        startY = 150
        spacingX = 150
        spacingY = 200
        rows, cols = 2, 5

        for i in range(len(app.quizRecommendations[:10])):
            songName, songData = app.quizRecommendations[i]
            col = i % cols
            row = i // cols
            x = startX + col * spacingX
            y = startY + row * spacingY

            if x <= mouseX <= x + 100 and y <= mouseY <= y + 100:
                app.song = songName
                app.artist = songData["artist"]
                mp3File = songData.get("file_path")
                if mp3File:
                    mixer.music.load(mp3File)
                    mixer.music.play()
                    app.isPlaying = True
                    app.playButtonGreen.fill = "red"
                    print(f"Playing: {songName} by {app.artist}")
                else:
                    print(f"MP3 file not found for {songName}")
                break

    if app.signedIn and app.signOutButton.contains(mouseX, mouseY):
        print(f"Signing out user: {app.user}")
        app.signedIn = False
        app.user = ''
        app.typingUser = True
        app.signInScreen = True
        app.chooseDirection = False
        app.mapOn = False
        app.byTopFive = False
        app.byQuiz = False
        app.showStatsPage = False
        app.whatIsHouseScreen = False
        app.showCoverImage = False
        app.shortCutScreen = False

    if app.showCoverImage:
        if app.playButtonGreen.contains(mouseX, mouseY):
            if app.isPlaying:
                mixer.music.pause()
                app.isPlaying = False
                app.playButtonGreen.fill = 'green'
                print("Song paused.")
            else:
                mixer.music.unpause()
                app.isPlaying = True
                app.playButtonGreen.fill = 'red'
                print("Song resumed.")

        elif app.skipButton.contains(mouseX, mouseY):
            skipToNextTrack(app)

        elif app.backButton.contains(mouseX, mouseY):
            skipToPreviousTrack(app)
        
        if app.recommendationsButton.contains(mouseX, mouseY):
            app.mapOn = False
            app.chooseDirection = False
            app.chooseQuiz = True
            app.byTopFive = False
            app.byQuiz = False
            app.showStatsPage = False
            app.whatIsHouseScreen = False
            app.showCoverImage = False
            app.shortCutScreen = False

def updateLikeButtonState(app):
    if app.song:
        profile = Profile(app.user)
        userData = profile.loadingData().get(app.user, {})
        likedSongs = userData.get("likedSongs", "").split(";")
        currentSong = f"{app.song.title} by {app.song.artist}".strip().lower()

        if currentSong in [song.strip().lower() for song in likedSongs]:
            app.heartButton.fill = 'red'
        else:
            app.heartButton.fill = 'grey'

def skipToNextTrack(app):
    print("skipToNextTrack called")
    if not app.selectedCity or not app.currentDecade:
        print("Skipping track failed: No city or decade selected.")
        return

    setCityAndDecade(app, app.selectedCity, app.currentDecade)

    songs = app.playlist.get(app.selectedCity, {}).get(app.currentDecade, [])
    if songs:
        app.currentSongIndex = (app.currentSongIndex + 1) % len(songs)
        nextSong = songs[app.currentSongIndex]

        try:
            mixer.music.load(nextSong.mp3File)
            mixer.music.play()
            app.song = nextSong
            app.isPlaying = True
            app.playButtonGreen.fill = 'red'

            app.currentCoverUrl = nextSong.imageUrl

            print(f"Now playing: {nextSong.title} by {nextSong.artist}")
        except Exception as e:
            print(f"Error skipping to next track: {e}")
    else:
        print(f"No songs available for {app.selectedCity} in the {app.currentDecade}.")


def skipToPreviousTrack(app):
    print("skipToPreviousTrack called")
    if not app.selectedCity or not app.currentDecade:
        print("Skipping track failed: No city or decade selected.")
        return

    songs = app.playlist.get(app.selectedCity, {}).get(app.currentDecade, [])
    if songs:
        app.currentSongIndex = (app.currentSongIndex - 1) % len(songs)
        previousSong = songs[app.currentSongIndex]

        try:
            mixer.music.load(previousSong.mp3File)
            mixer.music.play()
            app.song = previousSong
            app.isPlaying = True
            app.playButtonGreen.fill = 'red'

            app.currentCoverUrl = previousSong.imageUrl

            print(f"Now playing: {previousSong.title} by {previousSong.artist}")
        except Exception as e:
            print(f"Error skipping to previous track: {e}")
    else:
        print(f"No songs available for {app.selectedCity} in the {app.currentDecade}.")

    
    songs = app.playlist.get(app.selectedCity, {}).get(app.currentDecade, [])
    if songs:
        app.currentSongIndex = (app.currentSongIndex - 1) % len(songs)
        previousSong = songs[app.currentSongIndex]
        try:
            mixer.music.load(previousSong.mp3File)
            mixer.music.play()
            app.song = previousSong
            app.isPlaying = True
            app.playButtonGreen.fill = 'red'
            print(f"Now playing: {previousSong.title} by {previousSong.artist}")
        except Exception as e:
            print(f"Error skipping to previous track: {e}")
    else:
        print(f"No songs available for {app.selectedCity} in the {app.currentDecade}.")

def getCoverImage(spotify_client, songTitle, artistName):
    query = f"track:{songTitle.strip().lower()} artist:{artistName.strip().lower()}"
    results = spotify_client.search(q=query, type='track', limit=1)

    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        album_cover_url = track['album']['images'][0]['url']
        return album_cover_url
    else:
        print(f"No results found for {songTitle} by {artistName}.")
        return None

def importSongs(app): #Exception code is inspired by Exceptions 112 Lecture Notes
    try:
        trackNames = [songName for songName, feat in app.quizRecommendations]

        trackIds = app.quizRecommender.getSpotifyTrackIds(trackNames)

        if not trackIds:
            app.importMessage = "No valid tracks to add to the playlist."
            return

        userId = app.user
        playlistName = "My HOUSE RADIOOOOO Recommendations"
        playlistId = app.quizRecommender.createPlaylist(userId, playlistName)

        app.quizRecommender.addTracksToPlaylist(playlistId, trackIds)
        app.Message = f"Playlist '{playlistName}' created successfully! Added {len(trackNames)} tracks."
        print(app.Message)

    except Exception as e:
        print(f"Error creating playlist: {e}")

def forget_spotify_user(cache_path=".spotify_token_cache"):
    """Deletes the cache file to forget the most recent Spotify user."""
    if os.path.exists(cache_path):
        os.remove(cache_path)
        print("Spotify cache cleared. The app has forgotten the most recent user.")
    else:
        print("No Spotify cache found to clear.")

def authenticate_spotify(cache_path=".spotify_token_cache"): #Function inspired by https://spotipy.readthedocs.io/en/latest/#
    """Handles Spotify OAuth authentication."""
    forget_user = input("Do you want to forget the most recent user? (yes/no): ").strip().lower()
    if forget_user == "yes":
        forget_spotify_user()
    sp_oauth = SpotifyOAuth(
        scope="user-top-read playlist-read-private user-library-read playlist-modify-public playlist-modify-private",
        redirect_uri="https://localhost:8888/callback",
        client_id= "FILL IN"
        client_secret="FILL IN",
        cache_path=cache_path,
        open_browser=False
    )
    auth_url = sp_oauth.get_authorize_url()
    print(f"Please visit the following URL to authorize the application:\n{auth_url}")

    redirected_url = input("Paste the redirected URL here: ")
    code = sp_oauth.parse_response_code(redirected_url)
    token_info = sp_oauth.get_access_token(code)

    return spotipy.Spotify(auth=token_info['access_token'])

spotify_client = authenticate_spotify()

def playRecommendedSongs(app):
    if app.recommendedSongs:
        firstSong = app.recommendedSongs[0]
        app.song = firstSong
        mixer.music.load(firstSong.mp3File)
        mixer.music.play()
        app.isPlaying = True
        app.playButtonGreen.fill = 'red'
        print(f"Playing first recommended song: {firstSong.title} by {firstSong.artist}")

def getPastRecommendations(app):
    profile = Profile(app.user)
    userData = profile.loadingData().get(app.user, {})
    recommendedSongs = userData.get("recommendedSongs", "").split(";")
    return [song.strip() for song in recommendedSongs if song.strip()]

def getLikedSongs(app):
    profile = Profile(app.user)
    userData = profile.loadingData().get(app.user, {})
    likedSongs = userData.get("likedSongs", "").split(";")
    return [song.strip().title() for song in likedSongs if song.strip()]

def fetchLikedSongs(app, spotify_client):
    profile = Profile(app.user)
    userData = profile.loadingData().get(app.user, {})
    likedSongs = userData.get('likedSongs', '').split(';')

    app.likedSongs = []
    for likedSong in likedSongs:
        normalizedLikedSong = likedSong.strip().lower()
        if not normalizedLikedSong:
            continue
        for metadataTitle, metadata in app.musicMetadata.items():
            if metadata is None:
                print(f"Skipping invalid metadata for title: {metadataTitle}")
                continue
            if 'artist' not in metadata or 'city' not in metadata or 'decade' not in metadata:
                print(f"Skipping metadata missing required fields for title: {metadataTitle}")
                continue
            if metadataTitle.strip().lower() in normalizedLikedSong:
                coverImageUrl = metadata.get('imageUrl', None)
                if not coverImageUrl:
                    coverImageUrl = getCoverImage(spotify_client, metadataTitle, metadata['artist'])
                app.likedSongs.append({
                    'title': metadata.get('title', metadataTitle),
                    'artist': metadata['artist'],
                    'cover': coverImageUrl,
                    'file_path': metadata.get('file_path', ''),
                    'city': metadata.get('city', 'Unknown City'),
                    'decade': metadata.get('decade', 'Unknown Decade')
                })
                break

    print(f"Liked songs for user {app.user}: {app.likedSongs}")

def calculateUserAverageVector(userVectors):
    if not userVectors:
        return []

    numVectors = len(userVectors)
    vectorLength = len(userVectors[0])
    averageVector = [0] * vectorLength

    for vector in userVectors:
        for i in range(len(vector)):
            averageVector[i] += vector[i]
    return [value / numVectors for value in averageVector]

def generate_map_for_user(app):
    profile = Profile(app.user)
    userData = profile.loadingData().get(app.user, {})
    pastAnswers = userData.get("pastAnswers", "")
    user_vectors = [list(map(float, vec.split(','))) for vec in pastAnswers.split('|') if vec]

    if user_vectors:
        average_vector = calculateUserAverageVector(user_vectors)
        app.mapGenerator.generate_map_for_user(average_vector, output_image="user_similarity_map.png")
        app.mapImage = "user_similarity_map.png"
    else:
        print("No user vectors available to calculate similarity map.")

def navigateToScreen(app, newScreen):
    if app.currentScreen != "home":
        app.navigationStack.append(app.currentScreen)
    app.currentScreen = newScreen

def getScore(feat):
    return feat[1]["score"]
    
def setCityAndDecade(app, city, decade):
    app.selectedCity = city
    app.currentDecade = decade
    print(f"Set city to {city}, decade to {decade}")

def calculateButtonWidth(text, baseWidth=100, padding=20):
    textLength = len(text)
    return max(baseWidth, textLength * 10 + padding)

runApp(width=800, height=800)
