import keras
from sklearn.model_selection import train_test_split
import numpy as np
import h5py
from hyperas.distributions import choice, uniform

random_state = 12012002

def data():
    hf = h5py.File('drive/MyDrive/Cryptography/data_train.h5', 'r') 
    train_images = np.array(hf.get('x_train'))
    train_labels = np.array(hf.get('y_train'))

    # First we split training data set to 80% train 20% validate
    x_train, x_val, y_train, y_val = train_test_split(train_images, train_labels, test_size=0.2, random_state=random_state)

    x_train = x_train.astype('float32')
    x_val = x_val.astype('float32')

    # Standardizing/Normalizing the inputs 
    x_train /= 255
    x_val /= 255

    return x_train, y_train, x_val, y_val

def model(x_train, y_train, x_val, y_val):
	model = keras.Sequential() 
	model_choice = {{choice(['one', 'two'])}}
	if model_choice == 'one':
		model.add(keras.layers.Conv2D(16, kernel_size=3, activation='relu', padding='same', 
				                      input_shape=(100,100,3),data_format='channels_last'))
		model.add(keras.layers.Conv2D(16, kernel_size=3, activation='relu')) 
		model.add(keras.layers.MaxPooling2D(pool_size=2, strides=2)) 
		model.add(keras.layers.Dropout({{uniform(0, 1)}}))

		model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu'))
		model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu'))
		model.add(keras.layers.BatchNormalization())
		model.add(keras.layers.MaxPooling2D(pool_size=2, strides=2))

		model.add(keras.layers.Dropout({{uniform(0, 1)}})) 
	elif model_choice == 'two':
		model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu', padding='same', 
				                      input_shape=(100,100,3), data_format='channels_last'))
		model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu'))
		model.add(keras.layers.MaxPooling2D(pool_size=2, strides=2))
		model.add(keras.layers.Dropout({{uniform(0, 1)}}))

		model.add(keras.layers.Conv2D(64, kernel_size=3, activation='relu'))
		model.add(keras.layers.Conv2D(64, kernel_size=3, activation='relu'))
		model.add(keras.layers.BatchNormalization())
		model.add(keras.layers.MaxPooling2D(pool_size=2, strides=2))

		model.add(keras.layers.Dropout({{uniform(0, 1)}}))

	model.add(keras.layers. Flatten())
	model.add(keras.layers.Dense({{choice([256, 512, 1024])}}, activation='relu'))
	model.add(keras.layers.BatchNormalization())
	model.add(keras.layers.Dropout({{uniform(0, 1)}}))
	choiceval = {{choice(['one','two'])}}
	if choiceval == 'two':
		model.add(keras.layers.Dense({{choice([256, 512, 1024])}}, activation='relu'))
		model.add(keras.layers.BatchNormalization())
		model.add(keras.layers.Dropout({{uniform(0, 1)}}))
  
	model.add(keras.layers.Dense(2, activation='softmax'))

	adam = keras.optimizers.Adam(learning_rate=0.001)

	model.compile(loss='sparse_categorical_crossentropy', metrics=['accuracy'], optimizer=adam)
	model.fit(x_train, y_train, 
			  batch_size = 64, 
			  epochs = 30, verbose = 2, 
			  validation_data = (x_val, y_val))
	score, acc = model.evaluate(x_val, y_val, verbose = 0)
	return {'loss': -acc, 'status': STATUS_OK, 'model': model}