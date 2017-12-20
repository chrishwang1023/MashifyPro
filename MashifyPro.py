# Christopher Hwang, cjhwang
# Mashify Pro

import pyaudio
import pydub
from tkinter import *
import wave
import sys
import os
import soundcloud
import pygame
from pygame.locals import *
from pydub import AudioSegment
import threading
import PIL
from PIL import ImageTk, Image
import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
import urllib.request
import pickle

pygame.mixer.init(44100, -16,2,2048)

root = Tk()
buttonClick = 0 # "Make Sound" button pressed
soundOnHold = "" # Moment before recording
loading = 0 # "Loading" button pressed
deleting = 0 # "Delete" button pressed
filename = "" # Name of the file that will be inputted
message = [] 
files = []
startTime = 0
embed = []
streaming = 0
savedName = ""
openName = ""

# Background image of background
micImage = Image.open("mic drop.jpg")
mic = ImageTk.PhotoImage(micImage)

# Background image of system
discImage = Image.open("disc.jpg")
disc = ImageTk.PhotoImage(discImage)

# Background image of instructions
dj = Image.open("djdisc.jpg")
djdisc = ImageTk.PhotoImage(dj)

# Pad class for the recorded audio
class Pad(object):
    def __init__(self, audio):
        self.audio = audio

# Pad Color when box is clicked
class PadColor(object):
    def __init__(self, color):
        self.color = color
        self.text = "recorded"

def init(data, canvas):
    
    data.savedDoc = []

    # instance if it is a new project
    if data.savedDoc == []: 
        data.rows = 4 
        data.cols = 4
        data.margin = 100
        data.width = 800
        data.height = 600
        data.selected = Pad("")
        data.selection = [] # selected box coordinates
        data.board = [] # what the board has inside, name of audio wise
        data.soundBoard = [] # Whether the box is on or off

    # the tracks that are in store to play on the board
    # playingSounds lists are split up because pygame.Sound can only play 8
    # sounds at a time. The lists combine the sounds and play simulatneously.
    data.soundtracks = [] # the list of songs in audio form
    data.playingSounds = [] # audio to be played split up in 8's
    data.playingSounds2 = []
    data.playingSounds3 = []
    data.playingSounds4 = []
    data.playingSounds5 = []

    data.framePage = 0 # Frame page is the page it's on

    data.button = Button(canvas, text="Make Sound", command=button)
    data.givenSounds = Button(canvas,text="Record",
        command=soundButtons)
    data.loadingButton = Button(canvas, text="Load Sound", command=loadButton)
    data.deleteButton = Button(canvas, text="Delete Sound", command=delete)
    data.soundcloud = Button(canvas, text = "SoundCloud Stream", 
        command = stream)

    for row in range (data.rows): 
        data.board += [[None]*data.rows]
    for row in range (data.rows): 
        data.soundBoard += [["Off"]*data.rows]
    for row in range (data.rows): 
        data.soundtracks += [[None]*data.rows]

# Make Sound Button
def button():
    global buttonClick
    if buttonClick == 0:
        buttonClick = 1
    else:
        buttonClick = 0

# Record Button
def soundButtons():
    global buttonClick
    global soundOnHold
    global message 
    if buttonClick == 1:
        if soundOnHold == "":
            soundOnHold = "recording..."
        else: 
            soundOnHold = ""
    title = "Musical Qualities"
    response = choose(message, title)
    message = response

    # Process of reseting if there are not enough inputs to record
    if (response[0] == None and response[1] == None and response[2] == None and 
        response[3] == None and response[4] == None):
        buttonClick = 0
        soundOnHold = ""
        message = []

    # Another possibility of lack of inputs
    elif response[3] == None or (None not in [response[0], response[1], 
        response[2], response[4]]):
        buttonClick = 0
        soundOnHold = ""
        message = []

    else: 
        buttonClick = 1

# Button to load preexisting files
def loadButton():
    global loading
    global files
    if loading == 0:
        loading = 1
    elif loading == 1 or None in files:
        loading = 0
    title = "Load File"
    response = chooseFile(message, title)
    files = response
    if None in response:
        loading = 0
        files = []

# Button to delete audio on the board
def delete():
    global deleting
    if deleting == 0:
        deleting = 1
    elif deleting == 1:
        deleting = 0

# Button to stream from SoundCloud
def stream():
    global streaming
    global embed
    if streaming == 0:
        streaming = 1
    elif streaming == 1:
        streaming = 0
    title = "Enter embed #"
    response = embedNumber(message, title)
    embed = response
    if None in response:
        streaming = 0
        embed = []

# Button to save projects
def save(data):
    global savedName
    savedName = tkSimpleDialog.askstring("Save Project", "Name Project")
    data.savedDoc = [data.rows, data.cols, data.selected, data.selection, 
    data.board, data.soundBoard]
    pickle.dump(data.savedDoc, open(str(savedName) + ".p", 'wb'))

# Button to load preexisting projects
def load(data):
    global openName
    openName = tkSimpleDialog.askstring("Open Project", "Project Name")

    if not os.path.exists(openName + ".p"): tkMessageBox.showinfo("Error", 
        "File not in directory.")

    else: 
        data.savedDoc = pickle.load(open((openName) + ".p", 'rb'))
        # THe code below assigns the preexisting data into the project
        if len(data.savedDoc) > 0: 
            data.rows = data.savedDoc[0]
            data.cols = data.savedDoc[1]
            data.margin = 100
            data.width = 800
            data.height = 600
            data.selected = data.savedDoc[2]
            data.selection = data.savedDoc[3]
            data.board = data.savedDoc[4]
            data.soundBoard = data.savedDoc[5]
            for row in range(data.rows):
                for col in range(data.cols):
                    if data.board[row][col] != None:
                        data.soundtracks[row][col] = (pygame.mixer.Sound
                                (data.board[row][col].audio))
        else: 
            pass

# Text box and inputs for Recording
def choose(message, title):
    BPM = "BPM"
    response = tkSimpleDialog.askstring(title, BPM)
    meter = "Select Meter (x/4)"
    response2 = tkSimpleDialog.askstring(title,meter)
    bars = "Bars"
    response3 = tkSimpleDialog.askstring(title,bars)
    proj = "Name your audio" 
    response4 = tkSimpleDialog.askstring(title,proj)
    time = "Recording Time: "
    response5 = tkSimpleDialog.askstring(title,time)
    return [response, response2, response3, response4, response5]

# Text box and inputs for loading file
def chooseFile(message, title):
    loadingFile = 'File Name:'
    response = tkSimpleDialog.askstring(title, loadingFile)
    time = "Starting position in the audio:"
    response2 = tkSimpleDialog.askstring(title, time)
    time2 = "Ending position in the audio:"
    response3 = tkSimpleDialog.askstring(title,time2)
    newName = "New Trimmed Audio Name:"
    response4 = tkSimpleDialog.askstring(title, newName)
    return [response, response2, response3, response4]

# Text box and inputs for SoundCloud
def embedNumber(message, title):
    embedNum = 'Embed #: '
    response = tkSimpleDialog.askstring(title, embedNum)
    soundcloudFile = 'File Name: '
    response2 = tkSimpleDialog.askstring(title, soundcloudFile)
    startPoint = "Starting Point (in seconds): "
    response3 = tkSimpleDialog.askstring(title, startPoint)
    endPoint = "Ending Point (in seconds): "
    response4 = tkSimpleDialog.askstring(title, endPoint)
    trimmedClipFileName = "Trimmed Clip File Name: "
    response5 = tkSimpleDialog.askstring(title, trimmedClipFileName)
    return [response, response2, response3, response4, response5]

def mousePressed(event, data):
    # On the main Menu
    if data.framePage == 0:
        # if Mashify is pressed, go to the Mashify frame page
        if event.x >= 20 and event.x<=260 and event.y>=400 and event.y <= 480:
            data.framePage = 1
        # if Instructions is pressed, go to the instructions frame page
        elif event.x >= 20 and event.x<=270 and event.y>=534 and event.y <= 590:
            data.framePage = 2
        # if Load is pressed, execute the load function
        elif event.x >= 20 and event.x<=130 and event.y>=485 and event.y <= 520:
            load(data)

    # On the Mashify frame page
    elif data.framePage == 1:

        # Back to the Menu page
        if event.x>=10 and event.x<=150 and event.y>=30 and event.y<=60:
            data.framePage = 0

        # + and - arrows to adjust size of the board
        if event.x>=230 and event.x<=250 and event.y>=380 and event.y<=400:
            # Maximum dimension is 6 by 6
            if data.rows == 6:
                data.rows = 6
                data.cols = 6
            else:
                data.rows += 1
                data.cols += 1
                data.board = []
                data.soundBoard = []

            # Every time the dimension is changed, the board is reset
            for row in range(data.rows):
                data.board+=[[None]*data.rows]
            for row in range (data.rows): 
                data.soundBoard+=[["Off"]*data.rows]
            for row in range(data.rows):
                data.soundtracks += [[None]*data.rows]

        elif event.x>=230 and event.x<=250 and event.y>=420 and event.y<=440:
            data.soundtracks = []

            # Minimum dimension is 4 by 4
            if data.rows == 4 and data.cols == 4: 
                data.rows = 4
                data.cols = 4

            else:
                data.rows -= 1
                data.cols -= 1
                data.board = []
                data.soundBoard = []

            # reset the board every change
            for row in range(data.rows):
                data.board+=[[None]*data.rows]
            for row in range(data.rows):
                data.soundBoard+=[["Off"]*data.rows]

        # When the play button is pressed
        if event.x>=75 and event.x<=170 and event.y>=350 and event.y<=390:
            data.playingSounds = []
            
            # Make a big list of all the audios to be played
            for tracks in data.soundtracks:
                for sounds in tracks:
                    if sounds != None:
                        data.playingSounds.append((sounds))

                # The code below splits up the list of audios with 8 audios per
                # new list 
                if len(data.playingSounds) > 8 and len(data.playingSounds)<=16:
                    data.playingSounds2 = data.playingSounds[8:]
                else: 
                    data.playingSounds2 = data.playingSounds[8:16]

                if len(data.playingSounds) > 16 and len(data.playingSounds)<=24:
                    data.playingSounds3 = data.playingSounds[16:]
                else: 
                    data.playingSounds3 = data.playingSounds[16:24]

                if len(data.playingSounds) > 24 and len(data.playingSounds)<=32:
                    data.playingSounds4 = data.playingSounds[24:]
                else: 
                    data.playingSounds4 = data.playingSounds[24:32]

                if len(data.playingSounds) > 32 and len(data.playingSounds)<=36:
                    data.playingSounds5 = data.playingSounds[32:]

            # Playing and looping 
            for playSounds in data.playingSounds:
                playSounds.play(loops = -1)

        # When the stop button is pressed
        if event.x>=75 and event.x<=170 and event.y>=420 and event.y<=460:
            for playSounds in data.playingSounds:
                playSounds.stop()

    ########################################################################
    # Visualization of the grid according to the audios on the board

        (row, col) = getCell(event.x, event.y, data)
        row = int(row)
        col = int(col)

        global loading
        global soundOnHold
        global files

        # if the box already has an audio in it
        if ((row, col) in data.selection):
            if (data.board[row][col] != None):
                # Turning the boxes on and off for the audio to play or not
                if data.soundBoard[row][col] == "On":
                    data.soundBoard[row][col] = "Off"
                    data.soundtracks[row][col].set_volume(0)

                elif data.soundBoard[row][col] == "Off":
                    data.soundBoard[row][col] = "On"
                    data.soundtracks[row][col].set_volume(1)

            global deleting
            # When deleting, reset all elements related to that specific box
            if deleting == 1:
                data.selection.remove((row, col))
                data.board[row][col] = None
                data.soundBoard[row][col] = "Off"
                data.soundtracks[row][col] = None
                deleting = 0
        else:
        # if the box is empty
            if row != -1:
                global buttonClick
                global message
                # if ready to record
                if soundOnHold != "":
                    # add to the selected boxes list
                    data.selection += [(row, col)]

                    # criteria for recording 
                    if (None not in [message[0],message[1],message[2]] and 
                        message[4] == None) or (message[4] != None and None 
                        in [message[0], message[1], message[2]]):
                        record()
                        soundOnHold = filename
                        # add sound name to board
                        data.board[row][col] = Pad(soundOnHold)
                        # add audio type into the list of soundtracks
                        data.soundtracks[row][col] = (pygame.mixer.Sound
                            (soundOnHold))
                        data.soundBoard[row][col] = "On"
                        soundOnHold = ""
                        buttonClick = 0
                        message = []

                    else:
                        buttonClick = 0
                        soundOnHold = ""

                # ready to load preexisting files
                if loading == 1:
                    global files
                    fileName = files[0] + ".wav" #name of inputted desired file

                    # if file exists then store the audio info into data
                    if os.path.exists(fileName):
                        soundOnHold = fileName
                        trimLoadedClip(soundOnHold)
                        soundOnHold = files[3] + ".wav"
                        data.selection += [(row, col)]
                        data.board[row][col] = Pad(soundOnHold)
                        data.soundtracks[row][col] = (pygame.mixer.Sound
                            (soundOnHold))
                        data.soundBoard[row][col] = "On"
                        soundOnHold = ""
                        loading = 0
                        files = []

                    # message box if desired file doesn't exist
                    if not os.path.exists(fileName): 
                        loading = 0
                        tkMessageBox.showinfo("Error", 
                            "File not in directory.")

                global streaming
                # Streaming from SoundCloud
                if streaming == 1:
                    global embed
                    # first stream from SoundCloud and download the music
                    soundcloudStream()
                    fileName = embed[1] + ".wav"

                    # Double check to make sure file downlaoded 
                    if os.path.exists(fileName):
                        soundOnHold = fileName
                        # trim the clip at desired sections 
                        # and store info in data for that trimmed clip
                        trimClip(soundOnHold)
                        soundOnHold = embed[4] + ".wav"
                        data.selection += [(row, col)]
                        data.board[row][col] = Pad(soundOnHold)
                        data.soundtracks[row][col] = (pygame.mixer.Sound
                            (soundOnHold))
                        data.soundBoard[row][col] = "On"
                        soundOnHold = ""

                    if not os.path.exists(fileName): 
                        tkMessageBox.showinfo("Error", 
                            "File not in directory.")
                    embed = []
                    streaming = 0

        if event.x>=75 and event.x<=170 and event.y>=490 and event.y<=530:
            save(data) # save button clicked, save function runs

    elif data.framePage == 2:
        if event.x>=10 and event.x<=150 and event.y>=30 and event.y<=60:
            data.framePage = 0
        if event.x >= 62 and event.x<= 100 and event.y >= 320 and event.y<=345:
            data.framePage = 3

    elif data.framePage == 3:
        if event.x>=10 and event.x<=150 and event.y>=30 and event.y<=60:
            data.framePage = 2

def keyPressed(event,data):

    # simply runs the play function as if it was clicked when space is pressed
    if event.keysym == "space":
        if len(data.playingSounds) == 0:
            data.playingSounds = []
            for tracks in data.soundtracks:
                for sounds in tracks:
                    if sounds != None:
                        data.playingSounds.append((sounds))

                if len(data.playingSounds) > 8 and len(data.playingSounds)<=16:
                    data.playingSounds2 = data.playingSounds[8:]
                else: 
                    data.playingSounds2 = data.playingSounds[8:16]

                if len(data.playingSounds) > 16 and len(data.playingSounds)<=24:
                    data.playingSounds3 = data.playingSounds[16:]
                else: 
                    data.playingSounds3 = data.playingSounds[16:24]

                if len(data.playingSounds) > 24 and len(data.playingSounds)<=32:
                    data.playingSounds4 = data.playingSounds[24:]
                else: 
                    data.playingSounds4 = data.playingSounds[24:32]

                if len(data.playingSounds) > 32 and len(data.playingSounds)<=36:
                    data.playingSounds5 = data.playingSounds[32:]

            for playSounds in data.playingSounds:
                playSounds.play(loops = -1)

def timerFired(data):
    pass

def mouseMotion(event,data):
    pass

# Taken from 15-112 notes online
def getCell(x, y, data): # design of the board 
    if (not pointInGrid(x, y, data)): return (-1, -1)
    gridWidth  = 500
    gridHeight = 500
    cellWidth  = gridWidth / data.cols
    cellHeight = gridHeight / data.rows
    row = (y - 95) // cellHeight 
    col = (x - 255) // cellWidth
    # triple-check that we are in bounds
    row = min(data.rows-1, max(0, row))
    col = min(data.cols-1, max(0, col))
    return (row, col)

# Taken from 15-112 notes online
def getCellBounds(row, col, data):
    gridWidth  = 500
    gridHeight = 500
    columnWidth = gridWidth / data.cols 
    rowHeight = gridHeight / data.rows
    x0 = 255 + col * columnWidth
    x1 = 255 + (col+1) * columnWidth 
    y0 = 95 + row * rowHeight
    y1 = 95 + (row+1) * rowHeight
    return (x0, y0, x1, y1)

# Taken from 15-112 notes online
def pointInGrid(x, y, data):
    # return True if (x, y) is inside the grid defined by data.
    return ((255 <= x <= 755) and (95 <= y <= 595))

# Design for + and - buttons; play and stop buttons
def boardSizeController(canvas,data):
    canvas.create_rectangle(230,380,250,400, fill = "black")
    canvas.create_text(240,390, text="+", font = "arial 20", fill = "white")
    canvas.create_rectangle(230,420,250,440, fill = "black")
    canvas.create_text(240,430, text="-", font = "arial 20", fill = "white")

def playButton(canvas, data):
    canvas.create_rectangle(75, 350, 170, 390, fill = "sky blue")
    canvas.create_text(123, 370, text = "Play")

def stopButton(canvas, data):
    canvas.create_rectangle(75, 420, 170, 460, fill = "salmon")
    canvas.create_text(123, 440, text = "Stop")

def mainMenu(canvas, data):
    canvas.create_text(85,45, activefill = "blue", text = "Back to Menu", 
        font = "Sans 20 bold")

# Taken from pyaudio documentation and modified to fit the project
def record():
    global filename
    global message

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    
    # Options to record: inputting the time to record in seconds
    if message[3] != None and message[4] != None:
        RECORD_SECONDS = int(message[4])

    # Options to record: inputting BPM, meter and bar number
    elif (message[4] == None and message[0] != None and message[1] != None 
        and message[2] != None and message[3] != None):
            RECORD_SECONDS = (60/int(message[0])) * (
                int(message[1]))*(int(message[2]))

    filename = str(message[3]) + ".wav"
    
    WAVE_OUTPUT_FILENAME = filename
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Functions are from python3 documentation under urllib module
def soundcloudStream():
    global embed
    client = soundcloud.Client(client_id='7dbcff055170cdc49bc5f6d555009c39')
    track = client.get('/tracks/' + str(embed[0]))
    stream_url = client.get(track.stream_url, allow_redirects=False)
    url = stream_url.location
    wavfile = urllib.request.urlopen(url)
    with open(str(embed[1]) + ".wav", 'wb') as output:
        output.write(wavfile.read())

# Trims the clip between desired spots by seconds for loaded files
def trimLoadedClip(song):
    global files
    clip = AudioSegment.from_mp3(song)
    firstPoint = float(files[1]) * 1000
    secondPoint = float(files[2]) * 1000
    trimAudio = clip[firstPoint:secondPoint]
    trimAudio.export(files[3] + ".wav", 
        format="wav")

# Trims the clip from SoundCloud streaming directly
def trimClip(song):
    global embed
    clip = AudioSegment.from_mp3(song)
    firstPoint = float(embed[2]) * 1000
    secondPoint = float(embed[3]) * 1000
    trimAudio = clip[firstPoint:secondPoint]
    trimAudio.export(embed[4] + ".wav", 
        format="wav")

def redrawAll(canvas,data):
    # Main menu
    if data.framePage == 0:
        canvas.create_image(400, 310, image=mic)
        canvas.pack(side = TOP, expand=True, fill=BOTH)
        canvas.create_text(400,130,text = "Mashify Pro",font = "Sans 100 bold",
            fill = "white smoke")
        canvas.create_text(140,440, activefill = "orange", text = "Mashify", 
            font = "Sans 60 bold italic", fill = "white smoke")
        canvas.create_text(80, 500, activefill = "cyan", text = "Load", 
            font = "Sans 45 italic", fill = "white smoke")
        canvas.create_text(143,560, activefill = "salmon", 
            text = "Instructions",font = "Sans 45 italic",fill = "white smoke")

    # Mashify Page
    if data.framePage == 1:
        canvas.create_image(400,310, image=disc)
        canvas.pack(side = TOP, expand=True, fill=BOTH)

        for row in range(data.rows): # for each row of board
            for col in range(data.cols): # for each column of board
                (x0, y0, x1, y1) = getCellBounds(row, col, data)
                canvas.create_rectangle(x0,y0,x1,y1,fill="gray")

                if (row,col) in data.selection:
                    # Color selected boxes on the board with yellow
                    selected = PadColor("yellow")
                    if data.board[row][col] != None:
                        if data.soundBoard[row][col] == "On":
                            canvas.create_rectangle(x0,y0,x1,y1,
                                fill=selected.color)

        # Indicators for when the buttons are clicked
        if buttonClick != 0:
            canvas.create_rectangle(190,140,210,160,fill = "blue")
        else: 
            canvas.create_rectangle(190,140,210,160)

        if soundOnHold != "":
            canvas.create_rectangle(180,310,200,330,fill = "red")
        else: 
            canvas.create_rectangle(180,310,200,330)

        if loading != 0:
            canvas.create_rectangle(185,220,205,240,fill = "lime green")
        else: 
            canvas.create_rectangle(185,220,205,240)

        if deleting != 0:
            canvas.create_rectangle(190, 180, 210, 200, fill = "orange")
        else: 
            canvas.create_rectangle(190, 180, 210, 200)

        if streaming != 0:
            canvas.create_rectangle(210,262,230,282, fill = "purple")
        else: 
            canvas.create_rectangle(210,262,230,282)

        canvas.create_text(data.width/2 + 100,50,text="Mashify Pro",
            font = "Sans 50 bold", fill = "white smoke")

        # Buttons
        canvas.create_window(120,150,window = data.button)
        canvas.create_window(120,320,window = data.givenSounds)
        canvas.create_window(120,190,window = data.deleteButton)
        canvas.create_window(120,230,window = data.loadingButton)
        canvas.create_rectangle(75, 490, 170, 530, fill = "orange")
        canvas.create_text(123,510, text = "Save")
        canvas.create_window(120,275,window = data.soundcloud)

        boardSizeController(canvas, data)
        playButton(canvas,data)
        stopButton(canvas,data)
        mainMenu(canvas,data)

    # Instructions Page
    if data.framePage == 2:
        canvas.create_image(400,300, image=djdisc)

        canvas.create_text(85,45, activefill = "blue", text = "Back to Menu", 
        fill = "white", font = "Sans 20 bold")

        canvas.create_text(400,110, text = "How To Use Mashify Pro", 
            font = "Arial 60 bold", fill = "white smoke")

        canvas.create_rectangle(28,150,760,505, fill = "black")

        canvas.create_text(360,175, text = """
            Mashify Pro is a music production tool that develops beats by looping.
            """, fill = "orange", font = "Arial 21 bold")

        canvas.create_text(360,275, text = """
            Record, load a preexisting wave file, or stream from SoundCloud and
            store it to the sound board. To record, click the "Make Sound" button,
            then hit "Record". Insert the desired BPM, meter, number of bars, and 
            the recording name. Stream samples of music from SoundCloud. Click 
            """, fill = "salmon", font = "Arial 21 bold")

        canvas.create_text(65, 335, text = "here.", fill = "yellow", 
            font = "Arial 21 bold")

        canvas.create_text(362, 420, text = """
            Load wave files from the computer by clicking the "Load Sound" button
            and typing the name of the desired file.wav. 
            Click the sound board to turn on and off the desired sounds. Add more
            sounds to the board and make music! Save and load projects.
            """, fill = "sky blue", font = "Arial 21 bold")

    if data.framePage == 3:
        canvas.create_image(400,300, image=djdisc)
        canvas.create_text(115,45, activefill = "blue", 
            text = "Back to Instructions", fill = "white", font="Sans 20 bold")
        canvas.create_text(400,110, text = "How To Stream from SoundCloud", 
            font = "Arial 45 bold", fill = "white smoke")
        canvas.create_rectangle(18,210,790,375, fill = "black")
        canvas.create_text(360,285, text = """
            First, go to the desired SoundCloud track on the web. Click the share
            button under the track. Click 'Embed'. Under 'Code and Preview', find
            the series of numbers that follows "api.soundcloud.com/tracks/". 
            Enter that number. Enter the sample you want to add to your dj board
            by entering the starting and ending second marks of that sample!
            """, fill = "orange", font = "Arial 23 bold")


####################################
# run function 
####################################


def run(width=1000, height=600):

    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def mouseMotionWrapper(event, canvas, data):
        mouseMotion(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 10000 # milliseconds
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    init(data, canvas)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<B1-Motion>", lambda event:
                            mouseMotionWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(800,620)

