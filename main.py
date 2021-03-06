#!/usr/bin/python
from rgbmatrix import Adafruit_RGBmatrix
"""
class Adafruit_RGBmatrix(): # Debug environment
    def __init__(self, a=None, b=None): 
        return
    def Clear(self):
        return
    def SetImage(self, a, b, c):
        return
"""

import socket
origGetAddrInfo = socket.getaddrinfo
def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
    return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)
socket.getaddrinfo = getAddrInfoWrapper

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
import platform
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
        try:
            if ( platform.system() == "Darwin" ):
                self.font = ImageFont.truetype('/Library/Fonts/Arial Bold.ttf', 24)
            else:
                self.font = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf', 24)
        except:
            logging.debug( platform.system() )
            self.font = None;
        self.image_text = None
        self.news = None
        self.stock = None
        self.weather = None
        self.weatherlogo = None
        self.weathertext = None
        self.weathertime = os.path.getmtime("weather/weather.json")
        self.default = None
        
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
        self.stock_event = threading.Event()
        self.stock_event.clear()
        self.stop_prompt = threading.Event()
        self.stop_prompt.clear()

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
                #if self.stop_prompt.is_set() and self.input_event.is_set():
                if self.input_event.is_set():
                    logging.debug("New input while print. Continue: " + str(self.text) )
                    continue
                logging.debug("End printing input: " + str(self.text) )
                self.text = None
                # Back to print mode
                self.input_event.clear()
                self.stop_prompt.clear()
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
                self.stop_prompt.clear()
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
                self.nyan_event.clear()
                self.stop_prompt.clear()
                self.print_event.set()

            # Stock event
            elif self.stock_event.is_set():
                self.stop_prompt.clear()
                logging.debug("Printing stock: " + str(self.stock) )
                self.printStock()
                
                self.text = None
                self.setImage()
                self.stop_prompt.clear()
                logging.debug("End stock mode.")
                # Back to print mode
                self.stock_event.clear()
                self.stop_prompt.clear()
                self.print_event.set()

            # Print event
            elif self.print_event.is_set():
                self.stop_prompt.clear()
                self.print_event.wait()
                logging.debug("Printing default image: " + str(self.text))
                self.setImage()
                self.prompt()

            # Else (silent mode)
            else:
                logging.debug("No mode is turned on! Wait until print_event is on.")
                self.print_event.wait()
                    
    # Reload Image
    def reload(self):
        while not self.stop_event.is_set():
            self.print_event.wait()
            try:
                logging.debug("Reloading Image: " + str(self.image_text))
            except:
                logging.debug("Reloading Image/Not promptable")
            self.setWeather()
            #self.setImage()
            self.setDefaultImage()
            #self.image.save("testing2.png", "PNG")
            time.sleep(1)

            
    ############################################################
    # User Facing commands
    ############################################################
    def input(self, input):
        self.print_event.clear()
        self.news_event.clear()
        self.nyan_event.clear()
        self.stock_event.clear()
        self.stop_prompt.set()
        matrix.Clear()
        self.text = input
        self.input_event.set()

    def readNews(self):
        self.print_event.clear()
        self.nyan_event.clear()
        self.input_event.clear()
        self.stock_event.clear()
        self.stop_prompt.set()
        matrix.Clear()
        self.news_event.set()
        raw_input('News mode. Press anything to continue...')
        logging.debug("Exit news mode triggered")
        self.stop_prompt.set()
        #self.news_event.clear()

    def readStock(self):
        self.print_event.clear()
        self.news_event.clear()
        self.nyan_event.clear()
        self.input_event.clear()
        self.stop_prompt.set()
        matrix.Clear()
        self.stock_event.set()
        raw_input('Stock mode. Press anything to continue...')
        logging.debug("Exit stock mode triggered")
        self.stop_prompt.set()

    def reset(self):
        logging.debug("Return to regular state")
        matrix.Clear()
        self.input_event.clear()
        self.news_event.clear()
        self.nyan_event.clear()
        self.stock_event.clear()
        self.stop_prompt.set()
        self.print_event.set()


    def nyan(self):
        logging.debug("Nyan mode")
        self.print_event.clear()
        self.input_event.clear()
        self.news_event.clear()
        self.stock_event.clear()
        self.stop_prompt.set()
        self.nyan_event.set()
        matrix.Clear()

        
    def silent(self):
        self.print_event.clear()
        self.input_event.clear()
        self.news_event.clear()
        self.nyan_event.clear()
        self.stock_event.clear()
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
        userinput = default or "This is Akamai Cambridge Security Operation Command Center (SOCC). " + strftime("%H:%M:%S %Z", time.localtime()) + strftime(" (%H:%M:%S GMT)", time.gmtime())
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
        width = 10 + akamaiwidth + 10 + textwidth + 10 + raspwidth + 10
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

        
    def setDefaultImage(self):
        global akamailogo
        if self.default is None:
            self.setImage()
            self.default = self.image
        userinput = "This is Akamai Cambridge Security Operation Command Center (SOCC). " + strftime("%H:%M:%S %Z", time.localtime()) + strftime(" (%H:%M:%S GMT)", time.gmtime())
        text = self.textToImage(userinput)
        textloc1 = 10 + akamailogo.size[0] + 10
        textloc2 = 10 + akamailogo.size[0] + 10 + self.default.size[0] / 2
        self.image = self.default
        self.image.paste(text, (textloc1,0))
        self.image.paste(text, (textloc2,0))




        
    def setNews(self):
        self.news = None
        file = "news/news.json"
        key = "06e1a2dceeba46c89de4eecc8aaf24c0"
        #url = "https://newsapi.org/v1/articles?source=google-news&sortBy=top&apiKey=" + key
        url = "https://newsapi.org/v1/articles?source=the-next-web&sortBy=latest&apiKey=" + key
        duration = 60 * 30 # 30 Minutes
        filelastupdate = time.time() - os.path.getmtime(file)
        logging.debug("json file too old? " + str(filelastupdate ) + " > " + str(duration) + ": " + str(filelastupdate > duration))
        if filelastupdate  > duration: # json file too old?
            try:
                urllib.urlretrieve( url, file) # Try fetch json file
                logging.debug("Obtained news json.")
            except:
                logging.debug("Could not load article.")
        else:
            logging.debug("Using old json file.")
        # Get weather information
        try:
            newsfile = open(file)
            newsjson = json.load(newsfile)
            self.news = [entry["description"] for entry in newsjson["articles"]]
            #self.news = newsjson["articles"]
            logging.debug(str(self.news))
        except:
            logging.exception("ERROR!")
            logging.debug("Error loading json file")
            self.text = "Error loading json file."
        logging.debug("Ending print news")

    def setStock(self):
        self.stock = None
        file = "stock/stock.json"
        stocktype = ["INDEXDJX:%20.DJI", "INDEXNASDAQ:%20.IXIC", "INDEXSP:%20.INX", "NASDAQ%3aAKAM"]
        stocknames = ["INDEXDJX", "INDEXNASDAQ", "INDEXSP", "AKAM"]
        url = "https://finance.google.com/finance?output=json&q="
        duration = 60 * 10 # 10 Minutes
        filelastupdate = time.time() - os.path.getmtime(file)
        logging.debug("json file too old? " + str(filelastupdate) + " > " + str(duration) + ": " + str(filelastupdate > duration))
        if filelastupdate  > duration: # json file too old?
            stockdata = []
            try:
                for stock, stockname in zip(stocktype, stocknames):
                    stockname = "stock/" + stockname + ".json"
                    logging.debug("Obtaining stockname: " + stockname)
                    logging.debug("URL: " + url + stock)
                    data = urllib2.urlopen( url + stock ).read().replace("//", "")
                    stockdata.append(json.loads(data)[0])
                    logging.debug("Data persable.")
                with open(file, 'w') as filename:
                    json.dump(stockdata, filename, sort_keys=True, indent=4)
            except:
                logging.debug("Unable to obtain new json.")
        try:
            with open(file, 'r') as filename:
                stockjson = json.load(filename)
            stockname = ["DOW","NASDAQ","S&P","AKAM"]
            getlist = lambda x: [entry[x] for entry in stockjson]
            lists = [stockname, getlist("l"), getlist("c"), getlist("cp")]
            result = {z[0]:list(z[1:]) for z in zip (*lists)}
            self.stock = result
            logging.debug(str(self.stock))
        except:
            logging.exception("ERROR!")
            logging.debug("Error loading json file")
            self.text = "Error loading json file."
        logging.debug("Ending print stock")
            
    def setStockImage(self):
        global rasplogo,akamailogo, up, down
        # Set logo
        akamaiwidth = akamailogo.size[0]
        raspwidth = rasplogo.size[0]

        # Initial width
        width = 0
        self.image_text = ""
        imagelist = []

        for stockname, stockinfo in self.stock.iteritems():
            # Price
            price = stockname + " " + stockinfo[0] + " "
            self.image_text += price
            priceimage = self.textToImage(price, "white")

            # Price Change
            pricec = stockinfo[1] + " (" + stockinfo[2] + " %)"
            self.image_text += pricec
            color = "green" if float(stockinfo[1]) >= 0 else "red"
            updown = up if color is "green" else down
            pricecimage = self.textToImage(pricec, color)

            # Set width
            pricewidth = priceimage.size[0] + 10 + updown.size[0] + 10 + pricecimage.size[0]

            tempwidth = 10 + akamaiwidth + 10 + pricewidth + 10 + raspwidth + 10
            # Create image
            tempimage = Image.new("RGBA", (tempwidth, 32))
            width += tempwidth

            temp = 10
            tempimage.paste(akamailogo,(temp,0))
            temp += akamaiwidth + 10 
            tempimage.paste(priceimage, (temp,0))
            temp += priceimage.size[0] + 10
            tempimage.paste(updown, (temp,0))
            temp += updown.size[0] + 10
            tempimage.paste(pricecimage, (temp,0))
            temp += pricecimage.size[0] + 10
            tempimage.paste(rasplogo, (temp, 0))

            imagelist.append(tempimage)
        # Final image
        image = Image.new("RGBA", (width, 32))
        temp = 0
        for img in imagelist:
            image.paste(img, (temp, 0))
            temp += img.size[0]
        self.width = width
        self.image = image


    def setWeather(self, force=False):
        logging.debug("Set weather")
        now = time.time()
        duration = 60 * 30 # 30 Minutes
        file = "weather/weather.json"

        filelastupdate = time.time() - self.weathertime
        logging.debug("json: " + str(filelastupdate ) + " ?< " + str (duration) + " " + str(filelastupdate > duration))
        if filelastupdate > duration or force: # json file too old?
            try:
                weatherurl = "http://dataservice.accuweather.com/currentconditions/v1/329319?apikey=h7Z47DvD4mpW0b1iQzuL4sMLVgvc4PI6"
                urllib.urlretrieve( weatherurl, file) # Try fetch json file
                self.weathertime = os.path.getmtime(file)
            except:
                return
        else:
            logging.debug("Using old json file.")
            return # Won't load the json until the firs expire
        # Get weather information
        try:
            self.default = None # Used to update setDefaultImage
            weatherfile = open(file)
            weatherjson = json.load(weatherfile)[0]
            c_temp = weatherjson["Temperature"]["Metric"]["Value"]
            f_temp = weatherjson["Temperature"]["Imperial"]["Value"]
            weathertext = "{} F ({} C)".format(f_temp,c_temp)
            weatherimage = self.textToImage(weathertext)
            self.weathertext = weathertext
            self.weather = weatherimage
        except:
            logging.exception("ERROR!")
            logging.debug("Error loading json file")
            self.text = "Error loading json file."
            return

        # Weather icon
        #logging.debug("Try finding a logo...")
        url = "https://developer.accuweather.com/sites/default/files/"
        iconname = "{:0>2}-s.png".format(weatherjson["WeatherIcon"])
        if not os.path.isfile("weather/" + iconname): # Image not available?
            try:
                # Try fetch image file
                logging.debug("No weather logo! Try to fetch new...")
                urllib.urlretrieve( url+iconname, "weather/" + iconname)
                # Remove white color
                weatherlogo = Image.open("weather/" + str(iconname)).convert("RGBA")
                weatherlogo.thumbnail((60, 60), Imag.AeNTIALIAS)
                background = Image.new("RGBA",(32, 32),color=(255,255,255,0))
                background.paste(weatherlogo,(0,0),weatherlogo)
                weatherlogo.save("weather/" + iconname, "PNG")
                #weatherlogo.close()
            except Exception as ex:
                logging.debug("Something happened while try to fetch weather file.")
                logging.exception("ERROR!!")
                return
        weatherlogo = Image.open("weather/" + iconname).convert("RGBA")
        #logging.debug(str(weatherlogo))
        self.weatherlogo = weatherlogo

        
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

    def printStock(self):
        while True:
            self.setStock()
            self.setStockImage()
            self.text = self.image_text
            try:
                logging.debug("Printing stock: " + self.image_text + " " + str(self.width))
            except:
                logging.exception
            self.prompt(True, True, True)
            # If there are stock while prompt
            if self.stop_prompt.is_set() and self.stock_event.is_set():
                logging.debug("Exitting stock mode")
                return True
            elif self.stop_prompt.is_set():
                logging.debug("Going to other mode.")
                return True
            elif self.stock_event.is_set() is False:
                logging.debug("Stock mode ended.")
                return True
        logging.debug("Reached to the end of stock" )

    
    def printNyan(self):
        global nyan_list
        width = nyan_list[0].size[0]
        n = -width * 2/3
        temp_width = -width * 2/3
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

        
    def prompt(self, word=False, second=False, news=False):
        while not self.stop_event.is_set() or self.stop_prompt.is_set():
            if self.stop_prompt.is_set():
                return
            if second is False:
                    logging.debug("Start first loop!")
                    matrix.Clear()
            while not self.stop_prompt.is_set():
                start = 0 if second else SIZE
                end = -self.width if word else -self.width/2
                if word is True and second is True:
                    start = SIZE
                for n in range (start, end, -1):
                    # Exit if halted by event
                    matrix.SetImage(self.image.im.id, n, 0)
                    #logging.debug("prompting: " +str(n) + "/" + str(end))
                    self.stop_prompt.wait(self.sleep)
                    if self.stop_prompt.is_set():
                        return

                # If news, exit after the first cycle
                if news is True:
                    return

                # If not news, continue to make repeat
                if second is False:
                    if word is True:
                        logging.debug("Second word loop!")
                        self.prompt(True, True)
                        return
                    else:
                        logging.debug("Start second~ loop!")
                        self.prompt(False,True)
                        return


    #def textToImage(self, input, color="black"):
    def textToImage(self, input, color=128):
                text = textwrap.fill(input, 100)
                orig = Image.new("RGBA", (512,32))
                textsize = ImageDraw.Draw(orig).textsize(text, self.font)
                final = Image.new("RGBA", textsize)
                draw = ImageDraw.Draw(final)
                draw.text((0, 0), input, fill = color, font=self.font)
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

            up = Image.open("stock/up.png")
            down = Image.open("stock/down.png")

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
            if len(input) > 2500:
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
            elif input == "5" or input == "stock":
                thread.readStock()
            elif input == "8" or input == "nyan" or input == "cat":
                thread.nyan()
            elif input == "9" or input == "silent":
                thread.silent()
            elif input == "0" or input == "exit":
                thread.input("Exit? (y/n)")
                if raw_input('') is "y":
                    thread.stop()
                    time.sleep(5)
                    break
                thread.reset()
            elif input == "internet" or input == "network" or input == "net" or input == "connection":
                thread.input("Internet on?: " + str(internetOn()))
            elif input == "weather" or input == "updateweather":
                thread.setWeather(True)
            elif input == "counter" or input == "count" or input == "timer":
                input = raw_input('number: ')
                try:
                    timer = "...".join(str(i) for i in reversed(range(int(input)))) + "!"
                    thread.input(timer)
                except:
                    logging.debug("Invalid number")
            elif input == "":
                thread.reset()
            else:
                thread.input(input)
        except (KeyboardInterrupt, SystemExit):
                logging.exception("EXCEPTION")
                logging.debug("To exit, press 0 or 'exit'")
    logging.debug("Exitting... Goodbye!!")
        

                                
