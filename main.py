#!/usr/bin/python
from rgbmatrix import Adafruit_RGBmatrix

import Image
import ImageDraw
import ImageFont

import textwrap
from datetime import datetime
from time import gmtime, strftime
import time

import glob
import json
import logging
import os
import sys
import threading
import urllib, urllib2

logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

def internetOn():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=2)
        return True
    except urllib2.URLError as err:
        return False

class MainThread():
    ############################################################
    # Constructor
    ############################################################    
    def __init__(self):
        self.sleep = 0.01
        self.text = None
        self.font = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf', 24)
        self.image_text = None
        self.news = None
        self.weather = None
        self.weatherlogo = None
        self.weathertext = None
        
        ## Events
        self.stop_event = threading.Event()
        self.stop_event.clear()
        self.input_event = threading.Event()
        self.input_event.clear()
        self.news_event = threading.Event()
        self.news_event.clear()
        self.nyan_event = threading.Event()
        self.nyan_event.clear()
        self.print_event = threading.Event()
        self.print_event.set()
        self.stop_prompt = threading.Event()
        self.stop_prompt.clear()

        # Run Threads
        self.weather_thread = threading.Thread(target = self.setWeather, name = "Weather Thread")
        self.weather_thread.setDaemon(True)
        self.weather_thread.start()
        
        self.reload_thread = threading.Thread(target = self.reload, name = "Reload Thread")
        self.reload_thread.setDaemon(True)
        self.reload_thread.start()

        time.sleep(3)
        self.setImage()
        self.prompt_thread = threading.Thread(target = self.printout, name = "Prompt Thread")
        self.prompt_thread.setDaemon(True)
        self.prompt_thread.start()
        

    ############################################################
    # Thread settings
    ############################################################

    # Print Default
    def printout(self):
        while not self.stop_event.is_set():
            # Input event
            if self.input_event.is_set():
                self.stop_prompt.clear()
                logging.debug("Printing input: " + str(self.text) )
                self.setImage(self.text)
                self.prompt(True, False)
                
                # If there are input while prompt
                if self.stop_prompt.is_set() and self.input_event.is_set():
                    logging.debug("New input while print. Continue: " + str(self.text) )
                    continue
                elif self.stop_prompt.is_set():
                    logging.debug("Going to other mode.")
                    continue
                logging.debug("End printing input: " + str(self.text) )
                self.text = None
                # Back to print mode
                self.news_event.clear()
                self.nyan_event.clear()
                self.input_event.clear()
                self.print_event.set()

            # News event
            elif self.news_event.is_set():
                self.stop_prompt.clear()
                logging.debug("Printing news: " + str(self.text) )
                self.printNews()
                
                self.text = None
                self.setImage()
                self.stop_prompt.clear()
                logging.debug("End news mode.")
                # Back to print mode
                self.news_event.clear()
                self.nyan_event.clear()
                self.input_event.clear()
                self.print_event.set()

                
            # Nyan event
            elif self.nyan_event.is_set():
                self.stop_prompt.clear()
                logging.debug("Nyan event")
                self.printNyan()
                # If there are any input while prompt
                if self.stop_prompt.is_set() and self.nyan_event.is_set():
                    logging.debug("New nyan request while print. Continue" )
                    continue
                elif self.stop_prompt.is_set():
                    logging.debug("Going to other mode.")
                    continue
                logging.debug("End printing nyan" )
                # Back to print mode
                self.news_event.clear()
                self.nyan_event.clear()
                self.input_event.clear()
                self.print_event.set()

            # Print event
            elif self.print_event.is_set():
                self.print_event.wait()
                logging.debug("Printing default image: " + str(self.text))
                self.setImage()
                self.prompt()

                    
    # Reload Image
    def reload(self):
        while not self.stop_event.is_set():
            self.print_event.wait()
            logging.debug("Reloading Image: " + str(self.image_text))
            self.setImage()
            time.sleep(1)

            
    ############################################################
    # User Facing commands
    ############################################################
    def input(self, input):
        self.print_event.clear()
        self.news_event.clear()
        self.nyan_event.clear()
        self.stop_prompt.set()
        matrix.Clear()
        self.text = input
        self.input_event.set()

    def readNews(self):
        self.print_event.clear()
        self.nyan_event.clear()
        self.input_event.clear()
        self.stop_prompt.set()
        matrix.Clear()
        self.news_event.set()
        raw_input('News mode. Press anything to continue...')
        logging.debug("Exit news mode triggered")
        self.stop_prompt.set()
        #self.news_event.clear()


    def nyan(self):
        self.print_event.clear()
        self.input_event.clear()
        self.news_event.clear()
        self.stop_prompt.set()
        matrix.Clear()
        self.nyan_event.set()

    def silent(self):
        self.print_event.clear()
        self.input_event.clear()
        self.news_event.clear()
        self.nyan_event.clear()
        self.stop_prompt.set()
        matrix.Clear()
        raw_input('Silent mode. Press anything to continue...')
        self.stop_prompt.clear()
        self.print_event.set()

    def setSpeed(self, char):
        if char is "+":
                self.sleep -= 0.005 if self.sleep > 0.00005 else 0
                #self.sleep = self.sleep - 0.005 if self.sleep > 0.1 else 0.005
        if char is "-":
                self.sleep += 0.005 if self.sleep < 1 else 0
                #self.sleep = self.sleep + 0.05 if self.sleep < 5 else 4.95
        logging.debug(str(self.sleep))

    def stop(self):
        self.stop_event.set()
            
    ############################################################
    # Methods
    ############################################################
            
    def setImage(self, default=None):
                global rasplogo,akamailogo

                # Set word text
                userinput = default or "This is Akamai Security Operation Center (SOC). Current time is " + datetime.now().strftime("%H:%M:%S ") + strftime("%Z", gmtime())
                self.image_text = userinput
                text = self.textToImage(userinput)
                textwidth = text.size[0]

                # Set logo
                akamaiwidth = akamailogo.size[0]
                raspwidth = rasplogo.size[0]

                # Set weather
                weather = self.weather
                weatherlogo = self.weatherlogo
                weatherwidth = None if weather is None else weather.size[0] 
                weatherlogowidth = None if weatherlogo is None else weatherlogo.size[0]
                weathertext = None or self.weathertext
                if weathertext is not None:
                        self.image_text = userinput + " " + weathertext

                # Set width
                width = akamaiwidth + 10 + textwidth + 10 + raspwidth + 10
                width += weatherlogowidth + 10 + weatherwidth + 10 if weather is not None and weatherlogo is not None else 0
                width *= 2 if default is None else 1
                self.width = width

                # Create final image
                image = Image.new("RGBA", (width, 32))
                temp = 10
                image.paste(akamailogo,(temp,0))
                temp += akamaiwidth + 10 
                image.paste(text, (temp,0))
                temp += textwidth + 10
                image.paste(rasplogo, (temp, 0))
                if weather is not None and weatherlogo is not None and default is None:
                        temp += raspwidth + 10
                        image.paste(weather, (temp, 0))
                        temp += weatherwidth + 10
                        image.paste(weatherlogo, (temp, 0))
                if default is None:
                        image.paste(image, ( width/2 ,0))
                self.image = image
                

    def setNews(self):
            self.news = None
            key = "06e1a2dceeba46c89de4eecc8aaf24c0"
            url = "https://newsapi.org/v1/articles?source=google-news&sortBy=top&apiKey=" + key
            duration = 60 * 30 # 30 Minutes
            logging.debug("json file too old? " + str(time.time() - os.path.getmtime("news/news.json") ) + " > " + str(duration) + ": " + str(time.time() - os.path.getmtime("news/news.json") > duration))
            if time.time() - os.path.getmtime("news/news.json")  > duration: # json file too old?
            #if True: # json file too old?
                    if internetOn():
                            logging.debug("Internet is on.")
                            try:
                                    urllib.urlretrieve( url, "news/news.json") # Try fetch json file
                                    logging.debug("Obtained news json.")
                            except:
                                    logging.debug("Could not load article.")
                    else:
                            logging.debug("Internet is not on.")
                            self.text = "Internet is disabled."
            else:
                logging.debug("Using old json file.")
            try:
                    newsfile = open("news/news.json")
                    newsjson = json.load(newsfile)
                    self.news = [entry["description"] for entry in newsjson["articles"]]
                    #self.news = newsjson["articles"]
                    logging.debug(str(self.news))
            except:
                    logging.exception("ERROR!")
                    logging.debug("Error loading json file")
                    self.text = "Error loading json file."
            logging.debug("Ending print news")

            
    def setWeather(self):
            while not self.stop_event.is_set():
                    logging.debug("Set weather")
                    now = time.time()
                    duration = 60 * 30 # 30 Minutes
                    
                    logging.debug("json file timestamp (" + str(time.time() - os.path.getmtime("weather/weather.json") ) + ") less than duration (" + str (duration) + ")? " + str(time.time() - os.path.getmtime("weather/weather.json") > duration))
                    if time.time() - os.path.getmtime("weather/weather.json") > duration: # json file too old?
                            if internetOn(): # Internet connected?
                                    try:
                                            weatherurl = "http://api.wunderground.com/api/db42a9f158effdb7/conditions/q/MA/Cambridge.json"
                                            urllib.urlretrieve( weatherurl, "weather/weather.json") # Try fetch json file
                                    except:
                                            self.weather = None
                                            self.weathericon = None
                                            return
                            else:
                                    self.weather = None # No internet connection
                                    self.weathericon = None
                                    return

                    # Get weather information
                    weatherfile = open("weather/weather.json")
                    weatherjson = json.load(weatherfile)
                    weathertext = "Temp. " +  weatherjson["current_observation"]["feelslike_string"]
                    weatherimage = self.textToImage(weathertext)

                    self.weathertext = weathertext
                    self.weather = weatherimage

                    # Weather icon
                    logging.debug("Try finding a logo...")
                    url = weatherjson["current_observation"]["icon_url"]
                    iconname = url.split('/')[-1]
                    if not os.path.isfile("weather/s_" + str(iconname)): # Image not available?
                            try:
                                    # Try fetch image file
                                    logging.debug("No weather logo! Try to fetch new...")
                                    urllib.urlretrieve(weatherjson["current_observation"]["icon_url"], "weather/" + iconname)
                                    # Remove white color
                                    weatherlogo = Image.open("weather/" + str(iconname)).convert("RGBA")
                                    weatherlogo.thumbnail((32, 32), Image.ANTIALIAS)
                                    background = Image.new("RGBA",(32, 32),color=(255,255,255,0))
                                    background.paste(weatherlogo,(0,0),weatherlogo)
                                    weatherlogo.save("weather/s_" + str(iconname), "PNG")
                                    weatherlogo.close()
                            except Exception as ex:
                                    logging.debug("Something happened while try to fetch weather file.")
                                    logging.exception("ERROR!!")
                                    self.weather = None
                                    self.weathericon = None
                                    return
                    weatherlogo = Image.open("weather/s_" + str(iconname)).convert("RGBA")
                    logging.debug(str(weatherlogo))
                    self.weatherlogo = weatherlogo
                    time.sleep(duration)

                    
                                
            

        
    def printNews(self):
        while True:
            self.setNews()
            for news in self.news:
                self.text = str("[News] ") + news
                self.setImage(self.text)
                try:
                    logging.debug("Printing news: " + self.text)
                except:
                    logging.exception
                self.prompt(True, True, True)
                # If there are news while prompt
                if self.stop_prompt.is_set() and self.news_event.is_set():
                    logging.debug("Exitting news mode")
                    return True
                elif self.stop_prompt.is_set():
                    logging.debug("Going to other mode.")
                    return True
                elif self.news_event.is_set() is False:
                    logging.debug("News mode ended.")
                    return True
            logging.debug("Reached to the end of news" )

    
    def printNyan(self):
        global nyan_list
        width = nyan_list[0].size[0]
        n = -width * 2/3
        i = 0
        matrix.Clear()
        while n < 0:
            for file in nyan_list:
                matrix.SetImage(file.im.id, n, 0)
                n += 1
                if n == -width * 1/3 and i < 64:
                    n -= 1
                    i += 1
                self.stop_prompt.wait(0.045)
                if self.stop_prompt.is_set():
                        return
        logging.debug("Finish printing Nyan. Location: " + str(n) + "/" + str(width))

        
    def prompt(self, word=False, repeat=False, news=False):
            while not self.stop_event.is_set():
                start = 0 if repeat else SIZE
                end = -self.width if word else -self.width/2
                if word is True and repeat is True:
                    start = SIZE

                if repeat is False:
                        logging.debug("Start first loop! " + str(start) + " " + str(end))
                        matrix.Clear()
                while True:
                        for n in range (start, end, -1):
                                starttime = time.time()
                                # Exit if halted by event
                                matrix.SetImage(self.image.im.id, n, 0)
                                #logging.debug("prompting: " +str(n) + "/" + str(end))
                                self.stop_prompt.wait(self.sleep)
                                if self.stop_prompt.is_set():
                                        return
                        # If word, exit after the first cycle
                        if news is True:
                            return
                        
                        # If not word, continue to make repeat
                        if repeat is not True:
                            if word is True:
                                logging.debug("Second word loop!")
                                self.prompt(True, True)
                                return
                            else:
                                logging.debug("Start second~ loop!")
                                self.prompt(False,True)
                                return


    def textToImage(self, input):
                text = textwrap.fill(input, 100)
                orig = Image.new("RGBA", (512,32))
                textsize = ImageDraw.Draw(orig).textsize(text, self.font)
                final = Image.new("RGBA", textsize)
                draw = ImageDraw.Draw(final)
                draw.text((0, 0), input, fill = 128, font=self.font)
                return final
    
            

############################################################
# Main Thread
############################################################

if __name__ == '__main__':
        while True:
                try:
                        matrix = Adafruit_RGBmatrix(32, 4)
                        SIZE = 32 * 4
                        matrix.Clear()
                        
                        nyan_list = []
                        for filename in sorted(glob.glob('nyan/*.png'), key=lambda name: int(name[10:-4])):
                                logging.debug(filename)
                                im=Image.open(filename)
                                im.thumbnail((384, 32), Image.ANTIALIAS)
                                nyan_list.append(im)
                                
                        rasplogo = Image.open("rasplogo_s.png")
                        akamailogo = Image.open("akamailogo_s.png")

                        thread = MainThread()
                        logging.debug("Starting main thread.")
                except:
                        logging.exception("EXCEPTION")
                        break
                        continue
                break
        while True:
                try:
                        
                        input = raw_input('>>')
                        logging.debug("input: " + str(input))
                        if len(input) > 140:
                                pass
                        elif input == "-" or input == "+":
                                thread.setSpeed(input)
                        elif input == "1":
                                input = str("Cambridge is ready")
                                thread.input(input)
                        elif input == "2":
                                input = str("Cambridge has nothing to handover.")
                                thread.input(input)
                        elif input == "3":
                                input = str("HAVE A GOOD SHIFT!!")
                                thread.input(input)
                        elif input == "4" or input == "news":
                                thread.readNews()
                        elif input == "5" or input == "internet":
                                thread.input("Internet on?: " + str(internetOn()))
                        elif input == "8" or input == "nyan" or input == "cat":
                                thread.nyan()
                        elif input == "9" or input == "silent":
                                thread.silent()
                        elif input == "0" or input == "exit":
                                thread.input("Exit? (y/n)")
                                if raw_input('') is "y":
                                        thread.stop()
                                        break
                        else:
                                thread.input(input)
                except (KeyboardInterrupt, SystemExit):
                        logging.exception("EXCEPTION")
                        logging.debug("To exit, press 0 or 'exit'")
        logging.debug("Exitting... Goodbye!!")
        

                                
