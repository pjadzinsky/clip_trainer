""" keras_cnn.py


"""
import os
import tempfile

import boto3
import h5py

from clips import config

AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
BUCKET = config.BUCKET


def download_dataset_from_s3(key):
    assert(key.endswith('.hdf5'))

    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    _, temp_hdf5 = tempfile.mkstemp(suffix='.hdf5')
    client.download_file(BUCKET, key, temp_hdf5)

    return temp_hdf5


def load_features_and_labels(filename):
    """ First use download_dataset to get the s3 file to local drive.
    Then pass that file to this function to get 'features' and 'labels'
    """
    fid = h5py.File(filename, 'r')
    features = fid['features'][:]
    labels = fid['labels'][:]

    return features, labels


