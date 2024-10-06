import pandas as pd
import numpy as np
import glob
import cv2
from sklearn.model_selection import train_test_split
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Activation, Conv2D, Flatten, Dense, Dropout, MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator
from numpy.random import seed
seed(1337)
from tensorflow.random import set_seed
set_seed(1337)
import warnings
warnings.filterwarnings('ignore')


"""
Loading and resizing 2D images.
Parameters:
    pathX: path to the images folder
    pathY: path to the labels csv file
"""
def load_samples_as_images(pathX, pathY, img_width, img_height):
    files = sorted(glob.glob(pathX))
    labels_df = pd.read_csv(pathY)
    Y = np.array(labels_df[' hemorrhage'].tolist())
    images = np.empty((len(files), img_width, img_height))

    for i, _file in enumerate(files):
        images[i, :, :] = cv2.resize(cv2.imread(_file, 0), (img_width, img_height))

    return images, Y


"""
Train and use CNN model
Parameters:
    img_width: new size for the image width
    img_height: new size for the image height
    pathX: path to the images folder
    pathY: path to the labels csv file
"""
def cnnModel(img_width, img_height, pathX, pathY):
    # load the images and the labels:
    images, Y = load_samples_as_images(pathX, pathY, img_width, img_height)

    # split the dataset into train (80%), validation (10%) and test (10%) sets.
    train_images, test_images, train_labels, test_labels = train_test_split(images, Y, test_size=0.2, random_state=1)
    val_images, test_images, val_labels, test_labels = train_test_split(test_images, test_labels, test_size=0.5, random_state=1)

    # ----- Build the model: -----
    input_shape = (img_width, img_height, 1)
    model = Sequential()

    # First convolutional layer
    model.add(Conv2D(32, (3, 3), input_shape=input_shape))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # Second convolutional layer
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # Third convolutional layer
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # Flattening the result
    model.add(Flatten())

    # Dense layer
    model.add(Dense(64))
    model.add(Activation('relu'))

    # Dropout for regularization
    model.add(Dropout(0.5))

    # Output layer
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    # Compile the model
    model.compile(loss='binary_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])

    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        shear_range=0.0,
        zoom_range=0.1,
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True)

    # Data augmentation for validation
    val_datagen = ImageDataGenerator(rescale=1. / 255)

    train_generator = train_datagen.flow(
        train_images[..., np.newaxis],
        train_labels,
        batch_size=10)

    validation_generator = val_datagen.flow(
        val_images[..., np.newaxis],
        val_labels,
        batch_size=10)

    # Train the model
    history = model.fit_generator(
        train_generator,
        steps_per_epoch=len(train_images) // 10,
        epochs=100,
        validation_data=validation_generator,
        validation_steps=len(val_images) // 10)

    # Evaluate the model
    print("Final accuracy: " + str(model.evaluate(test_images[..., np.newaxis] / 255., test_labels)[1] * 100) + "%")

# Example call to the cnnModel function
cnnModel(img_width=320, img_height=320, pathX="path/to/images/*.png", pathY="path/to/labels.csv")

