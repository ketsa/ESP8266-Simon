# Project : ESP8266 - MICROPYTHON - MINI-SIMON
# Author : Mathias Chapuis
# Date : Janvier 2017

import machine; # for Pin and ? // might replace with from machine import...
import time;    # for PWM and timers, delays..
import urandom; # for random numbers generation
import ustruct; # for byte decoding i dont know about.

redled = machine.Pin(5, machine.Pin.OUT);
blueled = machine.Pin(4, machine.Pin.OUT);
greenled = machine.Pin(0, machine.Pin.OUT);
yellowled = machine.Pin(16, machine.Pin.OUT);
#yellowled.value(0); # fucking pin 16 starts HIGH...

beeper = machine.PWM(machine.Pin(14)); # beeper on pin 14

buttonred = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP);
buttonblue = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP);
buttongreen = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP);
buttonyellow = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP); # Funny micropython doesn't complain about PULL_UP. Doesnt work anyway, its pulled down and active HIGH.

melody = [100, 150, 200, 232, 262, 294, 330, 349, 392, 440, 494, 523, 900]; # maybe a melody later
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
    beeper.duty(0);

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
    #rndlist.clear();
    for i in range(x):
        rndlist.append(urandom.getrandbits(2));

def playrandomlist(randlist):
    for note in randlist:
        switchledon(note); # allumer la bonne led
        beeper.freq(notes[note]);
        beeper.duty(500);
        time.sleep(0.5);
        beeper.duty(0);
        switchledoff(note); # eteindre la bonne led
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

cod = uos.urandom(4); #get some true random number from uos.urandom because urandom.getrandbits slways give the same sequence...
decod = ustruct.unpack('BBBB', cod); # decode bytes into tuple of numbers.
urandom.seed(decod[0]); # seed urandom with a random number from uos.urandom...
# SHRINK 3 PREVIOUS LINES TO 1.

startupsequence();
time.sleep(1);

#times = 0;
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

    if buttonyellow.value()!=oldstate[3]:       # THIS ONE IS ACTIVE LOW
        time.sleep_ms(50); # lazy debounce
        if buttonyellow.value() == 1:           # THIS ONE IS ACTIVE LOW
            switchledon(3);
            playnote(3);
            oldstate[3]=buttonyellow.value();
        if buttonyellow.value() == 0:          # THIS ONE IS ACTIVE LOW
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

# rndlist.append(str(urandom.getrandbits(2))) # append a 0-3 random number to list

print("LOST - LOST - LOST - LOST - LOST - LOST - LOST - LOST - LOST - LOST");
