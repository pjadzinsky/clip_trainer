""" clip_generation.py

Download all individual images and generate a clip from them. Clip can be generated either forward or 
backwards
"""
import os
import numpy as np
import tempfile

from boto3.s3.transfer import S3Transfer
import boto3
import glob
from PIL import Image

AWS_ACCESS_KEY_ID = 'AKIAJ6MWTVEO2NFYGUMQ'
AWS_SECRET_ACCESS_KEY = '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'
PREFIX = "rotation"

def s3_download(clip_num):
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    transfer = S3Transfer(client)

    _, temp_file = tempfile.mkstemp(suffix=".png")

    frames = []
    for i in range(24):
        import pudb
        pudb.set_trace()
        print(temp_file)
        key = os.path.join(PREFIX, '{0}'.format(clip_num), '{0}.png'.format(i))
        transfer.download_file('geometrical-images', key, temp_file)
        frame = Image.open(temp_file)
        new_size = (1,) + frame.size + (3,)
        frame = np.array(list(frame.getdata())).reshape(new_size)
        frames.append(frame)

    return np.concatenate(frames)



if __name__ == "__main__":
    s3_download(1)
