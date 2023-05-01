from keras.models import load_model
import keras.utils as image
import h5py
import tensorflow as tf
import numpy as np
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

img_height = 100
img_width = 100

def check(url, model, res: list):
    image_path = screenshot(url)

    img = image.load_img(
        image_path, target_size=(img_height, img_width)
    )
    img_array = image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    class_names = ["clean", "defaced"]
    predictions = model.predict(img_array)
    
    if format(class_names[np.argmax(predictions[0])]) == "defaced":
        res.append("The website has been defaced")
    else:
        res.append("The website is safe")
    res.append(predictions[0][1])

def test(model):
    hf = h5py.File('data_test.h5', 'r') 
    test_data, test_labels = hf['x_test'], hf['y_test'] 

    model.evaluate(x=test_data, y=test_labels)

def screenshot(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument('--disable-dev-shm-usage') 
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1440x900")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
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

if __name__ ==  '__main__':
    our_model = load_model("./models/our_model.h5")
    # url = "http://localhost/dvwa/"
    url = "https://zonehmirrors.org/defaced/2023/03/24/dktambora.bimakab.go.id/dktambora.bimakab.go.id/1.txt"
    # url = "https://github.com/J4FSec/In0ri"

    print(check(url, our_model))