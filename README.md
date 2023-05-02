# Defacement-detection-app  
Application that employs CNN to detect defacement.  
Dataset is crawled from Zone.h including 1700 defaced and 2500 benign web screenshots.  

The crawler software is also an interesting aspect. It is also trained on CNN/Transformer to break Zone.h noisy captcha which in my opinion is extremely annoying.  
The crawler repo is at: https://github.com/duyvt6663/ZoneH.crawler.

The model components include:
* a CNN that acts as baseline classifier. 
* attack signatures matching.
* hash-based checking. (on-going)
# How to run  
```
pip install requirements.txt  
python main.py
```
 
---
Contact: duy.le1201@hcmut.edu.vn
