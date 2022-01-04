import schedule,time,random
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)
engine.setProperty('rate',160)

#Sentences = ["Way to go!", "Congratulations","You are the best","Keep going!","You are beautiful"]
#random.choice(Sentences)
def speak():
    with open('counter.txt') as f:
        global prev_value
        line_ = f.readlines()
        if line_[0] != prev_value and line_[0] != "0":
            engine.say("You skipped" + line_[0]+ "times")
            engine.runAndWait()
        prev_value  = line_[0]

prev_value = "0"
try:
    schedule.every(0.1).seconds.do(speak)
    while True:
        schedule.run_pending()
        #time.sleep(1)
except:
    pass