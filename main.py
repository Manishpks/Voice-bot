import speech_recognition as sr
import pyttsx3
import os
import subprocess
from subprocess import Popen, check_call
import beepy as b
from nltk import pos_tag
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from textblob import TextBlob
import geocoder
import requests, json

ps = PorterStemmer()
r = sr.Recognizer()


names = ("jessica")
end = ("goodbye","bye","bye bye","tata","goodnight","stop","bus","thank you")
what = ("what","how")
grocery = ("add","remove","show","clear","reset","grocery")

def end_func():
    return "goodbye"

def what_func(wh_tokens,noun_tokens):
    g = geocoder.ip('me')
    api_key="" #Add your api id from weatherapi.com
    response = requests.get("http://api.weatherapi.com/v1/current.json?key="+api_key+"&q="+g.city)
    x = response.json()
    return ("The temperature is "+str(x["current"]["temp_c"])+" degree celcius and it is "+x["current"]["condition"]["text"]+" outside.")
def grocery_func(verb,nouns):
    if "add" in verb:
        f = open("grocery.txt", "r")
        str = ","
        if "list" in nouns:
            nouns.remove("list")
        if "grocery" in nouns:
            nouns.remove("grocery")
        file = str.join(nouns)
        msg = f.read()
        f.close()
        f = open("grocery.txt","w")
        msg = msg.split(",")
        msg.extend(nouns)
        print(msg,set(msg))
        msg = list(set(msg))
        msg = str.join(msg)
        f.write(msg+",")
        f.close()
        return "Adding "+msg+" to grocery list"
    if "show" in verb:
        file_path = 'grocery.txt'
        if os.path.getsize(file_path) == 0:
            return "Your grocery list is empty"
        f1 = open("grocery.txt", "rt")
        msg = f1.read()
        msg1 = msg.split(',')
        if(len(set(msg1))==1):
            return "Your grocery list is empty"
        f1.close()
        return "You have "+msg+" in your grocery list"
    if "reset" in verb:
        f2 = open("grocery.txt", "r+")
        f2.truncate(0)
        f2.close()
        return "Grocery list cleared"
    if "remove" in verb:
        if "list" in nouns:
            nouns.remove("list")
        if "grocery" in nouns:
            nouns.remove("grocery")
        f3 = open("grocery.txt","r")
        msg = f3.read()
        f3.close()
        f3 = open("grocery.txt","w")
        msg = msg.split(",")
        ret=""
        for i in nouns:
            msg.remove(i)
            ret += i
        f3.write(','.join(msg)+",")
        f3.close()
        return "Removed "+ret+" from grocery list"

actions = {end:end_func,what:what_func,grocery:grocery_func}

def decide(command):
    tokens = word_tokenize(command)
    print(tokens)
    token_tag = pos_tag(tokens)
    # token_tag = TextBlob(command)
    print(token_tag)
    verb_tags = ['VBN', 'VBD','VB','WDT','WP','WP$','WRB']
    noun_tags = ['CD', 'NN', 'NNS', 'NNP', 'NNPS']
    verb_token = [tok for tok, tag in token_tag if tag in verb_tags]
    noun_tokens = [tok for tok,tag in token_tag if tag in noun_tags]

    for key in actions:
        try:
            if verb_token[0] in key:
                ret = actions[key](verb_token,noun_tokens)
                return ret
        except Exception as e:
            return e
    return "unknown"

def speakText(command):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-50)
    engine.say(command)
    engine.runAndWait()

def listen():
    try:
        with sr.Microphone() as source:
            # print(source2)
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.record(source,duration=5)
            command = r.recognize_google(audio,language="en-IN")
            command = command.lower()
            return command
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
    except sr.UnknownValueError:
        return "unknown"

def main():
    print("HERE")
    while(1):
        start=listen()
        print(start)
        if(start in names):
            b.beep(sound=5)
            command = ""
            while(command!="goodbye"):
                b.beep(sound=1)
                command=listen()
                # command = "what is the weather"
                print(command)
                if(command == "unknown"):
                    speakText("Sorry I did not get you")
                elif(command in end):
                    command = "goodbye"
                    continue
                else:
                    msg = decide(command)
                    if msg=="unknown":
                        speakText("Sorry I did not get you")
                    else:
                        print(msg)
                        speakText(msg)
            speakText("Goodbye")

main()
