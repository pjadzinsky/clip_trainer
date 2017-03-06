"""
continuous_s3_upload.py

This script is designed to upload all images in UNITY_ASSETS folder to s3

"""
import cPickle as pickle
import os
from PIL import Image
import tempfile

from boto3.s3.transfer import S3Transfer
import boto3
import glob

AWS_ACCESS_KEY_ID = 'AKIAJ6MWTVEO2NFYGUMQ'
AWS_SECRET_ACCESS_KEY = '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'
UNITY_ASSETS = '/Users/pablo/Documents/Unity/Rotating Objects/Assets/Images/rotation'
S3_PREFIX = 'rotation'


def s3_upload(filename):
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    transfer = S3Transfer(client)
    key = os.path.basename(filename).replace('_', '/')
    transfer.upload_file(filename, 'geometrical-images', key)


def to_numpy(clip_num):
    frames = []
    pngs = glob.glob(os.path.join(UNITY_ASSETS, '{0}_{1}_*.png'.format(S3_PREFIX, clip_num)))

    _, temp_file = tempfile.mkstemp(suffix=".png")

    frames = []
    array = None
    if len(pngs) == 24:
        for png in pngs:
            frame = Image.open(png)
            new_size = (1,) + frame.size + (3,)
            frame = np.array(list(frame.getdata())).reshape(new_size)
            frames.append(frame)

        array = np.concatenate(frames)

    with open(temp_file, 'wb') as fid:
        pickle(array, fid)

    return temp_file


def main():
    folders = glob.glob(os.path.join(UNITY_ASSETS, '*'))

    for folder in folders:
        pickled_array = to_numpy(folder)
        s3_upload(f)
        os.unlink(f)

        if os.path.isfile(f + ".meta"):
            os.unlink(f + ".meta")


if __name__ == "__main__":
    main()

