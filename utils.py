from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from keras.models import load_model
from selenium import webdriver
from threading import Thread
import keras.utils as image
from os.path import isfile
import tensorflow as tf
import numpy as np
import ahocorasick
import subprocess
import requests
import hashlib
import shutil
import glob
import json
import time
import os

img_height = 100
img_width = 100
dirr = './temp/'

################################################################
#                                                              #
#                          CHECKER CLASS                       #
#                                                              #
################################################################

class DefaceException(Exception):
    def __init__(self, alert, score=1) -> None:
        self.alert = alert
        self.score = score 
    
    def __str__(self) -> str:
        return self.alert
    
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
        self.gui.config_widgets('disabled')
        t.start()
    
    def monitor(self, url):
        self.url = url 

        t = Thread(target=self.add_url_to_hash_db)
        # disable gui and wait till checker finishes
        self.gui.config_widgets('disabled')
        t.start()

    def check_deface(self):
        try:
            self.check_signature()

            t1 = Thread(target=self.check_cnn)
            t2 = Thread(target=self.check_hash)
            t1.start(), t2.start()
            t1.join(), t2.join()

            # combine hash_point and cnn_point
            self.gui.label.config(text = "The website is safe")
            self.gui.progressbar.set_progress(.3*self.hash_safe_point+.7*self.cnn_safe_point)

        except DefaceException as e:
            self.gui.label.config(text = e.alert)
            self.gui.progressbar.set_progress(e.score)
            # print(e) 
        except:
            self.gui.label.config(text = "Something wrong with the URL")
        finally:
            # after finishing all check, enable the gui again
            self.gui.config_widgets('normal')

    def check_signature(self):
        data = requests.get(self.url).text
        if any(True for _ in self.automaton.iter(data)):
            raise DefaceException("Attack Signature Matched")
    
    def check_hash(self):
        with open('database/hashes.json', 'r+') as file:
            file_data = json.load(file)
            if file_data.get(self.url) is None:
                self.hash_safe_point = .15
                return #False
            
            hash_dict = self.get_files_hash()
            for key in hash_dict.keys():
                if file_data[self.url].get(key) != hash_dict.get(key):
                    raise DefaceException("Hash unmatched: "+key, .7)
                
            self.hash_safe_point = 0

    def check_cnn(self):
        try:
            image_path = screen_shot(self.url, self.gui)
        except Exception as e:
            print(e)
            print("URL " + self.url + " dead!")
            raise Exception("Something wrong")

        img = image.load_img(
            image_path, target_size=(img_height, img_width)
        )
        img_array = image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create a batch

        class_names = ["clean", "defaced"]
        predictions = self.model.predict(img_array)
        
        if format(class_names[np.argmax(predictions[0])]) == "defaced":
            alert = "The website has been defaced"
            raise DefaceException(alert, predictions[0][1])
        
        self.cnn_safe_point = predictions[0][1]

    def add_url_to_hash_db(self):
        hash_dict = self.get_files_hash()

        with open('database/hashes.json', 'r+') as file:
            file_data = json.load(file)
            file_data.update({self.url: hash_dict})
            # Sets file's current position at offset.
            file.seek(0)
            file.truncate()
            # convert back to json.
            json.dump(file_data, file, indent=4)
        
        # after finishing all check, enable the gui again
        self.gui.config_widgets('normal')
    
    def get_files_hash(self):
        shutil.rmtree(dirr, ignore_errors=True)
        os.mkdir(dirr)

        subprocess.run(['wget','-E', '-H', '-K','-k', '-p','-e', 'robots=off', '-P', dirr, self.url])

        dirs = glob.glob(dirr+'**', recursive=True)
        filenames = [f for f in dirs if isfile(f)]
        res = dict()
        for filename in filenames:
            if not is_external_file(filename):
                continue
            res.update({filename: md5(filename)})
            # print(filename, md5(filename))
        
        shutil.rmtree(dirr, ignore_errors=True)
        return res

################################################################
#                                                              #
#                         UTIL FUNCTIONs                       #
#                                                              #
################################################################

def screen_shot(url, gui=None):
    # get driver from gui if exist, else take new
    driver = get_driver() if gui.driver is None else gui.driver

    driver.get(url)
    print("Screenshoting..." + url)
    time.sleep(3)
    driver.save_screenshot("./images/temp.png")

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

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 20), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_external_file(filename):
    if '.css' in filename or\
       '.js' in filename or\
       '.jpg' in filename or\
       '.png' in filename or\
       '.svg' in filename or\
       '.ico' in filename:
        return True
    return False