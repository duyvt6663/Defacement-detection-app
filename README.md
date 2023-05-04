# Defacement-detection-app  
Application that employs CNN to detect defacement.  
Dataset includes 1700 defaced (crawled from Zone.h) and 2500 benign (Kaggle) web screenshots.  

The crawler software is also an interesting aspect. It was trained on CNN/Transformer to break Zone.h noisy captcha which in my opinion is extremely annoying.  
The crawler repo is at: https://github.com/duyvt6663/ZoneH.crawler.

The model components include:
* a CNN that acts as baseline classifier. 
* attack signatures matching.
* hash-based checking.

<p align="center">
 <img src="https://user-images.githubusercontent.com/93929554/235979928-705cb46e-0fc2-449a-a236-28ef56eda904.png" width="500">  
<p>
This hybrid model was adopted from [Hoang, X. D., & Nguyen, N. T. (2019). Detecting website defacements based on machine learning techniques and attack signatures. Computers, 8(2), 35.]

Our app as of its current state just simply receives a url and checks if it has high probability of having been defaced. It can, however, easily be modified to monitor urls intermittently.  

In hindsight, our CNN might not work very well since the dataset has quite a lot of overlaps, and the window size is 100x100 due to limit in memory. Will have to fix these later. 
# How to run  
```
pip install requirements.txt  
python main.py
```
 
---
Contact: duy.le1201@hcmut.edu.vn
