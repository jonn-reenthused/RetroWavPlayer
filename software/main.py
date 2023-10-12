from machine import Pin,SPI,PWM
import framebuf
import time
import os
import json
from wavePlayer import wavePlayer
import wave
import sdcard
import machine

# Retro Wave Player
# 2023 RE:Enthused

VERSION="0.1a"

# CONFIGURATION
# IS_DEMO will look for WAV files on the internal Pico memory if set to True
IS_DEMO = False
DEFPATH="sd"
BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9
SDCS = 17
SDSCK = 18
SDMOSI = 19
SDMISO = 16
UPIO = 7
DOWNIO = 6
SELECTIO = 5
BACKIO = 4
AUDIOLEFT = 20
AUDIORIGHT = 21
AUDIOGND = 22

upButton = ""
downButton = ""
selectButton = ""
backButton = ""

# GLOBALS
fileArray = []
currentScreen = 0
currentFile = ""
hasDisplayedWave = False
playMode = 0
currentPath = ""
currentPerc = 0
fileSeconds = 0.0
hasSDCard = False
player = wavePlayer() #None
currentMode = 0
selectDeBounce = False
backDeBounce = False
shouldReloadFiles = True

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 128

class LCD_1inch8(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 160
        self.height = 128
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
                
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        

        self.WHITE =   0xFFFF
        self.BLACK  =  0x0000
        self.GREEN   =  0x001F
        self.BLUE    =  0xF800
        self.RED   = 0x07E0

        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36);
        self.write_data(0x70);
        
        self.write_cmd(0x3A);
        self.write_data(0x05);

         #ST7735R Frame Rate
        self.write_cmd(0xB1);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);

        self.write_cmd(0xB2);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);

        self.write_cmd(0xB3);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);

        self.write_cmd(0xB4); #Column inversion
        self.write_data(0x07);

        #ST7735R Power Sequence
        self.write_cmd(0xC0);
        self.write_data(0xA2);
        self.write_data(0x02);
        self.write_data(0x84);
        self.write_cmd(0xC1);
        self.write_data(0xC5);

        self.write_cmd(0xC2);
        self.write_data(0x0A);
        self.write_data(0x00);

        self.write_cmd(0xC3);
        self.write_data(0x8A);
        self.write_data(0x2A);
        self.write_cmd(0xC4);
        self.write_data(0x8A);
        self.write_data(0xEE);

        self.write_cmd(0xC5); #VCOM
        self.write_data(0x0E);

        #ST7735R Gamma Sequence
        self.write_cmd(0xe0);
        self.write_data(0x0f);
        self.write_data(0x1a);
        self.write_data(0x0f);
        self.write_data(0x18);
        self.write_data(0x2f);
        self.write_data(0x28);
        self.write_data(0x20);
        self.write_data(0x22);
        self.write_data(0x1f);
        self.write_data(0x1b);
        self.write_data(0x23);
        self.write_data(0x37);
        self.write_data(0x00);
        self.write_data(0x07);
        self.write_data(0x02);
        self.write_data(0x10);

        self.write_cmd(0xe1);
        self.write_data(0x0f);
        self.write_data(0x1b);
        self.write_data(0x0f);
        self.write_data(0x17);
        self.write_data(0x33);
        self.write_data(0x2c);
        self.write_data(0x29);
        self.write_data(0x2e);
        self.write_data(0x30);
        self.write_data(0x30);
        self.write_data(0x39);
        self.write_data(0x3f);
        self.write_data(0x00);
        self.write_data(0x07);
        self.write_data(0x03);
        self.write_data(0x10);

        self.write_cmd(0xF0); #Enable test command
        self.write_data(0x01);

        self.write_cmd(0xF6); #Disable ram power save mode
        self.write_data(0x00);

        #sleep out
        self.write_cmd(0x11);
        #DEV_Delay_ms(120);

        #Turn on the LCD display
        self.write_cmd(0x29);

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x00)
        self.write_data(0xA0)
        
        
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x02)
        self.write_data(0x00)
        self.write_data(0x81)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

def is_hidden(file):
    return file.startswith('.')

def loadFileList(waveFolder):
    global currentIndex
    
    currentIndex = 0
    fileArray.clear()

    # get a list of .wav files
    files = os.ilistdir(waveFolder)
    
    for k in files:
        i = k[0]
        print(i)
        if is_hidden(i) == False:
            if k[1] & 0x4000: # Directory
                fileArray.append("[DIR] "+i)
            elif i.upper().find(".WAV") >= 0 and is_hidden(i) == False:
                fileArray.append(i)

    fileArray.sort()

def changeDirectory(directoryName):
    global currentPath
    global currentScreen
    global shouldReloadFiles
    
    directory = directoryName[5:].strip()
    currentPath = currentPath+ "/" + directory
    print(currentPath)
    
    shouldReloadFiles = True
    
    return True

def checkSelection(filename):
    # Check we aren't loading a directory
    if filename[0:5] == "[DIR]":
        return False
    else:
        return True

def loadWAV(filename):
    global fileSeconds
    global playMode
        
    try:
        f = wave.open(filename,'rb')
        fileSeconds = (f.getnframes() / f.getframerate())
        f.close()
    except:
        playMode = 2
        showWavStatus()

def showWavStatus():
    global playMode
    
    LCD.fill(LCD.WHITE)
    
    # Status Text
    statusText = ""
    statusColour = LCD.GREEN
    if playMode == 0:
        statusText = "PAUSED"
        statusColour = LCD.BLUE
    elif playMode == 1:
        statusText = "PLAYING"
        statusColour = LCD.GREEN
    elif playMode == 2:
        statusText = "ERROR"
        statusColour = LCD.RED
    else:
        statusText = "STOPPED"
        statusColour = LCD.RED
        
    putText(statusText, 60, 4, statusColour)
    
    # Filename
    putText(currentFile, 8, 20, LCD.BLACK)
    putText("{0:.2f} seconds".format(fileSeconds), 40, 40, LCD.BLACK)

    
    # Progress Bar
    #segment = int((SCREEN_WIDTH / 10) - 2)
    
    #LCD.rect(4, SCREEN_HEIGHT - (segment + 6), SCREEN_WIDTH - 7, segment + 4, LCD.BLUE)
    
    #for i in range(0, currentPerc):
    #    LCD.fill_rect((i * (segment + 1)) + 6, SCREEN_HEIGHT - (segment + 4), segment, segment, LCD.BLUE)
    
    LCD.show()


def putText(text, x, y, colour):
    LCD.text(text, x, y, colour)

def printText(text, x, y, inverted):
    if inverted:
        LCD.fill_rect(0,y,160,20,LCD.BLACK)
        putText(text, x, y + 8, LCD.WHITE)
    else:
        putText(text, x, y + 8, LCD.BLACK)

def showIntro():
    global VERSION
    
    putText("Retro Wave Player",8,8,LCD.BLUE)
    putText("Version: "+VERSION,8,24,LCD.BLUE)
    putText("2023 RE:Enthused",8,40,LCD.BLACK)
    putText("Finding Files",8,70,LCD.RED) 
    LCD.show()
    time.sleep(2)

def sdcardInit():
    hasSucceeded = False
    
    cs = machine.Pin(SDCS, machine.Pin.OUT)

    # Intialize the SD Card
    spi = machine.SPI(0,
                      baudrate=1000000,
                      polarity=0,
                      phase=0,
                      bits=8,
                      firstbit=machine.SPI.MSB,
                      sck=machine.Pin(SDSCK),
                      mosi=machine.Pin(SDMOSI),
                      miso=machine.Pin(SDMISO))
    
    try:
        sd = sdcard.SDCard(spi, cs)
        vfs = os.VfsFat(sd)
        os.mount(vfs, "/sd")
        
        hasSucceeded = True
    except Exception as error:
        hasSucceeded = False
    
    return hasSucceeded

def displayFileList(offset, maxOffset, fileArray, currentIndex):
    index = 0
    
    LCD.fill(LCD.WHITE)

    if len(fileArray) == 0:
        printText("no files found", 8, 8, False)
    
    if currentIndex >= len(fileArray):
        currentIndex = len(fileArray) - 1
    
    if currentIndex < 0:
        currentIndex = 0
    
    if currentIndex > maxOffset:
        offset = currentIndex - maxOffset
    else:
        offset = 0
        
    if currentIndex < offset:
        offset = offset - 1

    for file in range(offset, min(offset + (maxOffset + 1), len(fileArray))):
        filename = fileArray[file]
        if len(filename) > 18:
            filename = filename[0:18]
        
        if file == currentIndex:
            printText(filename, 8, (index * 17), True)
        else:
            printText(filename, 8, (index * 17), False)
            
        index = index + 1

def stopWAV():
    global playMode
    
    if playMode == 1:
        player.stop()
        playMode = 0

def playWAV():
    global hasDisplayedWave
    global currentFile
    global playMode
    global player
    
    if playMode == 2:
        return
    
    if hasDisplayedWave == False:
        return
    
    playMode = 1
    showWavStatus()
    time.sleep(1)
    
    try:
        player.play(currentFile)
        stopWAV()
    except KeyboardInterrupt:
        stopWAV()
    
def processButtons():
    global upButton
    global downButton
    global selectButton
    global backButton
    global currentScreen
    global currentIndex
    global currentMode
    global currentFile
    global hasDisplayedWave
    global selectDeBounce
    global playMode

    if shouldReloadFiles:
        return

    if upButton.value() == 0:
        if currentScreen == 0:
            currentIndex = currentIndex - 1
            return True
    elif downButton.value() == 0:
        if currentScreen == 0:
            currentIndex = currentIndex + 1
            return True
    elif selectButton.value() == 0:
        if selectDeBounce == False:
            selectDeBounce = True
            if currentScreen == 0:
                currentFile = fileArray[currentIndex]
                if checkSelection(currentFile) == True:
                    hasDisplayedWave = False
                    currentMode = 0
                    currentScreen = 1
                else:
                    print("Directory Changed")
                    return changeDirectory(currentFile)
            elif currentScreen == 1:
                if currentMode == 0 and hasDisplayedWave:
                    playWAV()
    elif backButton.value() == 0:
        if currentScreen == 1:
            if playMode == 0 or playMode == 2:
                currentScreen = 0
                return True
            else:
                stopWAV()
                playMode = 0

    if selectButton.value() == 1:
        selectDeBounce = False

    return False

def get_config_default(file):
    global BL
    global DC
    global RST
    global MOSI
    global SCK
    global CS
    global SDCS
    global SDCSCK
    global SDMOSI
    global SDMISO
    global UPIO
    global DOWNIO
    global SELECTIO
    global BACKIO
    global AUDIOLEFT
    global AUDIORIGHT
    global AUDIOGND
    global currentScreen
    
    try:
        with open(file) as fd:
            config = json.load(fd)
            
            BL = config["DISP_BL_PIN"]
            DC = config["DISP_DC_PIN"]
            RST = config["DISP_RST_PIN"]
            MOSI = config["DISP_MOSI_PIN"]
            SCK = config["DISP_SCK_PIN"]
            CS = config["DISP_CS_PIN"]
            SDCS = config["SD_CS_PIN"]
            SDCSCK = config["SD_SCK_PIN"]
            SDMOSI = config["SD_MOSI_PIN"]
            SDMISO = config["SD_MISO_PIN"]
            UPIO = config["UP_PIN"]
            DOWNIO = config["DOWN_PIN"]
            SELECTIO = config["SELECT_PIN"]
            BACKIO = config["BACK_PIN"]
            AUDIOLEFT = config["AUDIO_LEFT_PIN"]
            AUDIORIGHT = config["AUDIO_RIGHT_PIN"]
            AUDIOGND = config["AUDIO_GND_PIN"]
        
    except OSError:
        with open(file, "w") as fd:
            config = {
                "DISP_BL_PIN": BL,
                "DISP_DC_PIN": DC,
                "DISP_RST_PIN": RST,
                "DISP_MOSI_PIN": MOSI,
                "DISP_SCK_PIN": SCK,
                "DISP_CS_PIN": CS,
                "SD_CS_PIN": SDCS,
                "SD_SCK_PIN": SDSCK,
                "SD_MOSI_PIN": SDMOSI,
                "SD_MISO_PIN": SDMISO,
                "UP_PIN": UPIO,
                "DOWN_PIN": DOWNIO,
                "SELECT_PIN": SELECTIO,
                "BACK_PIN": BACKIO,
                "AUDIO_LEFT_PIN": AUDIOLEFT,
                "AUDIO_RIGHT_PIN": AUDIORIGHT,
                "AUDIO_GND_PIN": AUDIOGND,
            }
            json.dump(config, fd)
            return config

def processBackButton(pin):
    global playMode
    global currentScreen
    
    if currentScreen == 1:
        if playMode == 1:
            stopWAV()

if __name__=='__main__':
    # Initialise Starting Conditions
    currentScreen = 0
    shouldReloadFiles = False
    shouldDisplayFiles = True

    hasSDCard = sdcardInit()
    
    if IS_DEMO:
        DEFPATH = ""
        hasSDCard = True
        
    currentPath = DEFPATH
    
    if hasSDCard:
        get_config_default(DEFPATH+"/config")
        shouldReloadFiles = True
     
    #TODO: Whilst testing comment this out so the player can initialise at the top of the app
    #player = wavePlayer(leftPin=Pin(AUDIOLEFT),rightPin=Pin(AUDIORIGHT), virtualGndPin=Pin(AUDIOGND))
    
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535

    currentIndex = 0
    offset = 0
    maxOffset = 6

    upButton = Pin(UPIO, mode=Pin.IN, pull=Pin.PULL_UP)
    downButton = Pin(DOWNIO, mode=Pin.IN, pull=Pin.PULL_UP)
    selectButton = Pin(SELECTIO, mode=Pin.IN, pull=Pin.PULL_UP)
    backButton = Pin(BACKIO, mode=Pin.IN, pull=Pin.PULL_UP)

    backButton.irq(trigger=Pin.IRQ_FALLING, handler=processBackButton)

    LCD = LCD_1inch8()
    #color BRG
    LCD.fill(LCD.WHITE)
    showIntro() 

    forward = True
    
    try:
        while True:
            shouldDisplayFiles = processButtons()
            if shouldReloadFiles:
                print("Loading Files")
                loadFileList(currentPath)
                shouldReloadFiles = False
                shouldDisplayFiles = True
                
            if hasSDCard == False:
                hasSDCard = sdcardInit()
                if hasSDCard == False:
                    LCD.fill(LCD.WHITE)
                    printText("no sd card", 8, 8, False)
                    LCD.show()
                    time.sleep(2)
                else:
                    get_config_default(DEFPATH+"/config")
                    shouldReloadFiles = True
                    currentScreen = 0
            elif currentScreen == 0:
                if len(fileArray) == 0:
                    shouldReloadFiles = True
                
                if shouldDisplayFiles:
                    displayFileList(offset, maxOffset, fileArray, currentIndex)
                    shouldDisplayFiles = False
                    LCD.show()
                    time.sleep(0.5)
                    LCD.fill(0xFFFF)
            elif currentScreen == 1:
                showWavStatus()
                currentPerc = currentPerc + 1
                if currentPerc > 10:
                    currentPerc = 0
                if hasDisplayedWave == False:
                    LCD.fill(LCD.WHITE)
                    LCD.show()
                    loadWAV(fileArray[currentIndex])
                    hasDisplayedWave = True
    except KeyboardInterrupt:
        stopWAV()
        print("wave player terminated")



