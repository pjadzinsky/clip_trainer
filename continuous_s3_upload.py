"""
continuous_s3_upload.py

This script is designed to upload all images in UNITY_ASSETS folder to s3

When running Unity code, we generate
/Users/pablo/Documents/Micelaneous/Scripts/Unity_support/Images/rotation/<number>/*.png

This script will (given a 'number' identifying a folder with images):
    load all images as numpy arrays
    concatenate them along dimension 0  (making a 4D array, time, width, height, RGB)
    upload them to s3

"""
import _pickle as pickle
import os
from PIL import Image
import tempfile

from boto3.s3.transfer import S3Transfer
import boto3
import glob
import numpy as np

import config

AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
UNITY_ASSETS = config.UNITY_ASSETS
S3_PREFIX = config.S3_PREFIX

def s3_upload(filename, key):
    """ Upload local file 'filename' to s3 using S#_PREFIX/<name> format """
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    transfer = S3Transfer(client)
    print("About to upload: {0}".format(key))
    transfer.upload_file(filename, 'geometrical-images', key)
    print("\tdone uploading")


def pickle_numpy(folder, size):
    """ load all png images under folder, convert each to a numpy array and return the concatenation
    of all of them. Returned array has one extra dimension than each png since they are concatenated
    allong dimension 0 representing time

    Before concatenating all pngs we clip to the center part of each image, extracted patch will be
    of shape size x size
    """
    frames = []
    pngs = glob.glob(os.path.join(folder, '*.png'))

    _, temp_file = tempfile.mkstemp(suffix=".png")

    frames = []
    array = None
    if len(pngs) == 24:
        for png in pngs:
            frame = Image.open(png)
            width, height = frame.size
            new_size = (1, width, height, 3)
            frame = np.array(list(frame.getdata())).reshape(new_size)

            x0 = width // 2 - size // 2
            x1 = x0 + size
            y0 = height // 2 - size // 2
            y1 = y0 + size
            frame = frame[:, x0:x1, y0:y1, :] 
            frames.append(frame)

        array = np.concatenate(frames)

    with open(temp_file, 'wb') as fid:
        pickle.dump(array, fid)

    print('size of ndarray is {0}'.format(array.shape))
    return temp_file


def clean(folder):
    import pudb
    pudb.set_trace()
    files = glob.glob(os.path.join(folder, '*'))

    for f in files:
        os.unlink(f)

    os.rmdir(folder)


def main():
    """ For each folder under UNITY_ASSETS (each folder contains 24 pngs)
        convert all 24 pngs to a numpy array of shape (1, 24, width, height, RGB)
        pickle the array to a local file
        upload the local file to s3 under something like rotation/00010.pkl
    """
    # figure out all the folders of the from UNITY_ASSETS/#, each one contains all png images
    # forming a clip
    folders = glob.glob(os.path.join(UNITY_ASSETS, '*'))

    for i, folder in enumerate(folders):
        pickled_array = pickle_numpy(folder, 128)
        key = os.path.join(S3_PREFIX, "{0}".format(i).zfill(5) + '.pkl')

        s3_upload(pickled_array, key)
        clean(folder)
        

if __name__ == "__main__":
    main()

