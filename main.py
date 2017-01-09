# Project : ESP8266 - MICROPYTHON - MINI-SIMON
# Author : Mathias Chapuis
# Date : Jan. 2017

import machine; # for Pin and ? // might replace with from machine import...
import time;    # for PWM and timers, delays..
import urandom; # for random numbers generation
import ustruct; # for byte decoding i dont know about.

redled = machine.Pin(5, machine.Pin.OUT);
blueled = machine.Pin(4, machine.Pin.OUT);
greenled = machine.Pin(0, machine.Pin.OUT);
yellowled = machine.Pin(16, machine.Pin.OUT);
#yellowled.value(0); # fucking pin 16 starts HIGH ?

beeper = machine.PWM(machine.Pin(14)); # beeper on pin 14

buttonred = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP); # Buttons
buttonblue = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP);
buttongreen = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP);
buttonyellow = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP); 
# Funny micropython doesn't complain about pin 15 declared PULL_UP. Doesnt work anyway, its pulled down and active HIGH.

melody = [100, 150, 200, 232, 262, 294, 330, 349, 392, 440, 494, 523, 900]; # maybe add melody later
notes = [216, 433, 649, 866];
rndlist=[]; # init a list for our random numbers.
btlist=[]; # and a list of buttonpresses.

lost = False;

#beeper = machine.PWM(machine.Pin(14, machine.Pin.OUT), freq=440, duty=512); 


def startupsequence():
    beeper = machine.PWM(machine.Pin(14));
    beeper.duty(500);
    for herz in range(150, 1000):
        beeper.freq(herz);
        if herz < 300:
            redled.value(1);
        if (herz > 300 and herz < 500):
            blueled.value(1);
        if (herz > 500 and herz < 750):
            greenled.value(1);
        if (herz > 750 and herz < 999):
            yellowled.value(1);
        time.sleep(0.002);

#    for note in notes:
#        beeper.freq(note);
#        time.sleep(0.5);

    for herz in range(150, 1000):
        beeper.freq(1000-herz);
        time.sleep(0.002);
        if herz < 300:
            redled.value(0);
        if (herz > 300 and herz < 500):
            blueled.value(0);
        if (herz > 500 and herz < 750):
            greenled.value(0);
        if (herz > 750 and herz < 999):
            yellowled.value(0);
    beeper.duty(0); # I still have some strange noise from the beeper even when duty=0...

def switchledon(led):
    if led==0:
        redled(1);
    elif led==1:
        blueled(1);
    elif led==2:
        greenled(1);
    elif led==3:
        yellowled(1);

def switchledoff(led):
    if led==0:
        redled(0);
    elif led==1:
        blueled(0);
    elif led==2:
        greenled(0);
    elif led==3:
        yellowled(0);

def randomlist(x):
    for i in range(x):
        rndlist.append(urandom.getrandbits(2));

def playrandomlist(randlist):
    for note in randlist:
        switchledon(note); 
        beeper.freq(notes[note]);
        beeper.duty(500);
        time.sleep(0.5);
        beeper.duty(0);
        switchledoff(note);
        time.sleep(0.2);

def playnote(note):
    beeper.freq(notes[note]);
    beeper.duty(500);

def playmelody(note):
    beeper.freq(note);
    beeper.duty(500);

def getbuttonstates():
    return [buttonred.value(), buttonblue.value(), buttongreen.value(), buttonyellow.value()];

def comparelists():
    global lost;
    print(rndlist);
    print(btlist);

    for i in range(len(btlist)):
        if btlist[i] != rndlist[i]:
            lost=True;

    print(lost);

cod = uos.urandom(4); #get some random number from uos.urandom because urandom.getrandbits give the same sequence every reset...
decod = ustruct.unpack('BBBB', cod); # decode bytes into tuple of numbers.
urandom.seed(decod[0]); # seed urandom with a random number from uos.urandom...
# Could SHRINK 3 PREVIOUS LINES TO 1.

startupsequence();
time.sleep(1);

randomlist(1);
playrandomlist(rndlist);
oldstate = getbuttonstates();

while not lost:

    if buttonred.value()!=oldstate[0]:
        time.sleep_ms(50); # lazy debounce
        if buttonred.value() == 0:
            switchledon(0);
            playnote(0);
            oldstate[0]=buttonred.value();
        if buttonred.value() == 1:
            btlist.append(0);
            comparelists();
            switchledoff(0);
            beeper.duty(0);
            oldstate[0] = buttonred.value();

    if buttonblue.value()!=oldstate[1]:
        time.sleep_ms(50); # lazy debounce
        if buttonblue.value() == 0:
            switchledon(1);
            playnote(1);
            oldstate[1]=buttonblue.value();
        if buttonblue.value() == 1:
            btlist.append(1);
            comparelists();
            switchledoff(1);
            beeper.duty(0);
            oldstate[1] = buttonblue.value();

    if buttongreen.value()!=oldstate[2]:
        time.sleep_ms(50); # lazy debounce
        if buttongreen.value() == 0:
            switchledon(2);
            playnote(2);
            oldstate[2]=buttongreen.value();
        if buttongreen.value() == 1:
            btlist.append(2);
            comparelists();
            switchledoff(2);
            beeper.duty(0);
            oldstate[2] = buttongreen.value();

    if buttonyellow.value()!=oldstate[3]:       # Pin 15 : This one is active LOW.
        time.sleep_ms(50); # lazy debounce
        if buttonyellow.value() == 1:           # ACTIVE LOW
            switchledon(3);
            playnote(3);
            oldstate[3]=buttonyellow.value();
        if buttonyellow.value() == 0:          # ACTIVE LOW
            btlist.append(3);
            comparelists();
            switchledoff(3);
            beeper.duty(0);
            oldstate[3] = buttonyellow.value();

    if len(btlist) == len(rndlist) and not(lost):
        randomlist(1);
        time.sleep(1);
        playrandomlist(rndlist);
        btlist=[];


if lost:
    for note in melody[::-1]:
        playmelody(note);
        time.sleep_ms(200);
    time.sleep(1);
    machine.reset();

# add :  several modes, speed, keep longest streak ? ...


