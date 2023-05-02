from keras.models import load_model
import keras.utils as image
import tensorflow as tf
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from threading import Thread
import requests
import ahocorasick

img_height = 100
img_width = 100

class Checker:
    def __init__(self, gui) -> None:
        self.gui = gui
        self.model = load_model("./models/our_model.h5")

        self.build_dict()
    
    def build_dict(self):
        # init the automaton
        self.automaton = ahocorasick.Automaton()

        file = open("database/signatures.json", "r")
        signatures = json.load(file)
        for index, sig in enumerate(signatures):
            self.automaton.add_word(sig, (index, sig))
        self.automaton.make_automaton()

    def check(self, url):
        self.url = url 

        t = Thread(target=self.check_deface)
        # disable gui and wait till checker finishes
        self.gui.url.config(state='disabled')
        t.start()

    def check_deface(self):
        try:
            self.check_signature()
            self.check_cnn()
        except DefaceException as e:
            self.gui.label.config(text = e.alert)
            self.gui.progressbar.set_progress(e.score)
            # print(e) 
        except:
            self.gui.label.config(text = "Something wrong with the URL")
        finally:
            # after finishing all check, enable the gui again
            self.gui.url.config(state='normal')

    def check_signature(self):
        data = requests.get(self.url).content.decode("utf-8")
        if any(True for _ in self.automaton.iter(data)):
            raise DefaceException("Attack Signature Matched")

    def check_cnn(self):
        image_path = screen_shot(self.url, self.gui)

        img = image.load_img(
            image_path, target_size=(img_height, img_width)
        )
        img_array = image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create a batch

        class_names = ["clean", "defaced"]
        predictions = self.model.predict(img_array)
        
        if format(class_names[np.argmax(predictions[0])]) == "defaced":
            alert = "The website has been defaced"
        else:
            alert = "The website is safe"

        raise DefaceException(alert, predictions[0][1])

################################################################
#                                                              #
#                         UTIL FUNCTIONs                       #
#                                                              #
################################################################

def screen_shot(url, gui=None):
    try:
        # get driver from gui if exist, else take new
        driver = get_driver() if gui is None else gui.driver

        driver.get(url)
        print("Screenshoting..." + url)
        # time.sleep(3)
        driver.save_screenshot("./images/temp.png")
        driver.quit()
    except Exception as e:
        print(e)
        print("URL " + url + " dead!")
        raise Exception("Something wrong")

    return "./images/temp.png"

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument('--disable-dev-shm-usage') 
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1440x900")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

class DefaceException(Exception):
    def __init__(self, alert, score=1) -> None:
        self.alert = alert
        self.score = score 
    
    def __str__(self) -> str:
        return self.alert