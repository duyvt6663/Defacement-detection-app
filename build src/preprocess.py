from PIL import Image
import os 
import numpy as np
import h5py
from random import sample
from sklearn.model_selection import train_test_split
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

defaced_path = "..\\Dataset\\Defaced\\"
benign_path = "..\\Dataset\\Benign\\"
random_state = 12012002

def get_one_image(path):
    rgba_image = Image.open(path)
    image_data = rgba_image.convert('RGB')
    return image_data

def get_dataset_images(defaced_path, benign_path, in_dim = (100, 100), num_channels=3):
    # list files from both defaced and benign datasets
    defaced_files = os.listdir(defaced_path)
    benign_files = os.listdir(benign_path)

    num_files = len(defaced_files)+len(benign_files)
    labels = np.zeros(shape=num_files, dtype=np.uint8)
    dataset = np.zeros(shape=(num_files, in_dim[0], in_dim[1], num_channels))

    index = 0
    # create output labels and input data (images) for files
    for file in defaced_files:
        dataset[index] = get_one_image(defaced_path+file)
        labels[index] = 1 # defaced = 1
        index += 1
    
    for file in benign_files:
        dataset[index] = get_one_image(benign_path+file)
        labels[index] = 0 # benign = 0
        index += 1
    
    # return input data and output labels
    return dataset, labels

def resize_images(*paths):
    # resize images in paths to 100x100
    for path in paths:
        for image_name in os.listdir(path):
            img = Image.open(path+image_name)
            new_img = img.resize((100, 100))
            new_img.save(path+image_name)

def split_dataset(defaced_path, benign_path, split_factor = .2):
    dataset, labels = get_dataset_images(defaced_path, benign_path)

    train_labels, test_labels,\
    train_indices, test_indices = train_test_split(labels, range(len(labels)), 
                                                   test_size=split_factor, 
                                                   random_state=random_state)

    train_images, test_images = dataset[train_indices], dataset[test_indices]
    return train_images, train_labels, test_images, test_labels

if __name__ ==  '__main__': 
    # super time intensive, consider multithread next time this is used
    resize_images(benign_path) # this option will be discarded after the 1st time it runs

    train_images, train_labels,\
    test_images, test_labels = split_dataset(defaced_path, benign_path)

    hf = h5py.File('data_train.h5', 'w') 
    hf.create_dataset('x_train', data=train_images)
    hf.create_dataset('y_train', data=train_labels) 
    hf.close()

    hf = h5py.File('data_test.h5', 'w') 
    hf.create_dataset('x_test', data=test_images) 
    hf.create_dataset('y_test', data=test_labels)
    hf.close()