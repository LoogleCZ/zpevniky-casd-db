from PyPDF2 import PdfReader
import re

lines = []
lastCm = []
lastTm = []
currentLine = ""

def visitor_text_extractor(text, cm, tm, fontDict, fontSize):
    global lines
    global lastCm
    global lastTm
    global currentLine
    if(cm == lastCm and tm == lastTm):
        currentLine = currentLine + text
    else:
        lastCm = cm
        lastTm = tm
        lines.append(currentLine)
        currentLine = text

def processSong(reader, pageNum):
    global lines
    global lastCm
    global lastTm
    global currentLine
    page = reader.pages[pageNum]

    lines = []
    page.extract_text(visitor_text=visitor_text_extractor)

    lines = [line.strip() for line in lines if line.strip() != ""]

    notes = [
        'C',
        'D',
        'E',
        'F',
        'G',
        'A',
        'H',
        'B'
    ]

    specifications = [
        'maj',
        'mi',
        'm',
        'sus',
        '#',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '10',
        '11',
        '12',
        '13'
    ]

    outline = []
    for line in lines:
        clean = False
        for word in re.split(" |\/|\(|\)", line):
            word = word.strip()
            word = word.strip(":")
            if(word == ""):
                continue
            for specification in specifications:
                word = word.replace(specification, '')
            if word not in notes:
                clean = True
                break
        if(clean == True):
            outline.append(line)

    songName = ""
    songNumber = 0
    songAuthor = ""
    chorus = ""
    bridge = ""
    verses = []
    verse = ""
    verseNum = 0
    readVerse = False
    readChorus = False
    readBridge = False
    bridgeStart = 0
    chorusStart = 0
    for line in outline:
        if(line.startswith("autor: ")):
            songAuthor = line.replace("autor: ", "")
            continue
        x = re.search("^([0-9]*)\. (.*)$", line)
        if(x):
            songNumber = x.group(1)
            songName = x.group(2)
            continue
        if(line == "Ref.:"):
            readVerse = False
            readChorus = True
            readBridge = False
            chorus = ""
            if(verse != ""):
               verses.append(verse)
            verse = ""
            chorusStart = verseNum
            continue
        if(line == "Bridge:"):
            readVerse = False
            readChorus = False
            readBridge = True
            bridgeStart = verseNum
            bridge = ""
            if(verse != ""):
               verses.append(verse)
            verse = ""
            continue
        x = re.search("^([0-9]+).$", line)
        if(x):
            readVerse = True
            readChorus = False
            readBridge = False
            if(verse != ""):
               verses.append(verse)
            verse = ""
            print(songName)
            verseNum = int(x.group(1))
            continue
        if(readVerse):
            verse = verse + line + "\n"
        if(readChorus):
            chorus = chorus + line + "\n"
        if(readBridge):
            bridge = bridge + line + "\n"

    if(verse != ""):
        verses.append(verse)
    finalText = ""
    arrangement = ""
    i = 1
    chorusInserted = False
    bridgeInserted = False
    for verse in verses:
        finalText = finalText + "[V" + str(i) + "]\n"
        finalText = finalText + verse + "\n"
        arrangement = arrangement + "V" + str(i) + " "
        if(bridgeStart <= i and bridge != ""):
            if(bridgeInserted == False):
                finalText = finalText + "[B]\n"
                finalText = finalText + bridge + "\n"
            bridgeInserted = True
            arrangement = arrangement + "B "
        if(chorusStart <= i and chorus != ""):
            if(chorusInserted == False):
                finalText = finalText + "[C]\n"
                finalText = finalText + chorus + "\n"
            chorusInserted = True
            arrangement = arrangement + "C "
        i = i + 1

    f = open("../NaHoru dolů spolu/" + str(songNumber) + " " + songName, "w")
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<song>
    <title>{}</title>
    <copyright></copyright>
    <hymn_number>{}</hymn_number>
    <lyrics><![CDATA[
{}
]]>
    </lyrics>
    <presentation>{}</presentation>
    <author>{}</author>
    <ccli></ccli>
    <capo print="false"></capo>
    <key></key>
    <aka></aka>
    <key_line></key_line>
    <user1></user1>
    <user2></user2>
    <user3></user3>
    <theme></theme>
    <tempo></tempo>
    <time_sig></time_sig>
</song>
""".format(songName, songNumber, finalText, arrangement.strip(), songAuthor))
    f.close()



reader = PdfReader('zpevnik_nahoru_dolu_spolu_2019.pdf')
# processSong(reader, 19)
for i in range(42):
    processSong(reader, i+2)


