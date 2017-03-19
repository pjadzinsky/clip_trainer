""" keras_cnn.py


"""
import os
import tempfile

from keras.layers import Activation
from keras.layers import Dense
from keras.layers.convolutional import Conv3D
from keras.layers.core import Flatten
from keras.models import Sequential

from clips import utils

model = Sequential()
model.Add(Conv3D(3, 3, 1, "same", 32, input_dim=784))
model.Add(Activation('relu'))
model.Add(Flatten())
model.Add(Dense(2))
model.Add(Activation('softmax'))

# For a binary classification problem
model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# Train the model, iterating on the data in batches of 32 samples
#filename = download_dataset_from_s3('clips.hdf5')
features, labels = utils.load_features_and_labels('test.hdf5')
print(features.shape)
print(labels.shape)
model.fit(features, labels, epochs=2, batch_size=1)
