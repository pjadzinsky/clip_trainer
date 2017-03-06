""" clip_generation.py

Download all individual images and generate clips from them.
All clips are concatenated into a 4D numpy array and are played forward, if you want to played them
backwards you have to reverse the example along the dimension 0 (time)

"""
import numpy as np
import os
import sys
import tempfile

from boto3.s3.transfer import S3Transfer
import boto3
import gflags
import glob
import h5py
from PIL import Image

AWS_ACCESS_KEY_ID = 'AKIAJ6MWTVEO2NFYGUMQ'
AWS_SECRET_ACCESS_KEY = 'lOAFFbMUG55IYqVdKYy1we9eSKSguEm/VUJN1NjJ'
PREFIX = 'rotation'
BUCKET = 'geometrical-images'

gflags.DEFINE_integer('samples', None, 'number of clips to download from aws s3')

FLAGS = gflags.FLAGS


def download_one_clip_from_s3(clip_num):
    """ Download all images corresponding to one clip and concatenate them along dim 0
    Each frame is 3D (width, height, RGB), after concatenating them they are 4D
    (time, width, height, RGB)
    """
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    transfer = S3Transfer(client)

    _, temp_file = tempfile.mkstemp(suffix=".png")

    frames = []
    for i in range(24):
        key = os.path.join(PREFIX, '{0}'.format(clip_num), '{0}.png'.format(i))
        transfer.download_file(BUCKET, key, temp_file)
        frame = Image.open(temp_file)
        new_size = (1,) + frame.size + (3,)
        frame = np.array(list(frame.getdata())).reshape(new_size)
        frames.append(frame)

    return np.concatenate(frames)


def create_numpy(samples):
    """ Download 'samples' from aws, convert each to numpy and concatenate along dim 0, 
    output will be 5D (sample, time, width, height, RGB)
    """
    clips = []
    for sample in range(1, samples + 1):
        print('Downloading clip {0}/{1}'.format(sample, samples))
        clip = download_one_clip_from_s3(sample)
        clip = np.expand_dims(clip, 0)
        clips.append(clip)

    return np.concatenate(clips, 0)


def count_aws_objects():
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    paginator = client.get_paginator('list_objects')

    page_iterator = paginator.paginate(Bucket=BUCKET, Prefix=PREFIX)
    import pudb
    pudb.set_trace()

    return len(list(page_iterator))


if __name__ == "__main__":
    print(count_aws_objects())
    exit(0)
    try:
        argv = FLAGS(sys.argv)  # parse flags
    except gflags.FlagsError as e:
        print('%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS))
        sys.exit(1)

    if FLAGS.samples:
        samples = FLAGS.samples
    else:
        samples = count_aws_objects()

    clips = create_numpy(FLAGS.samples)

    with h5py.File('examples.hdf5', 'w') as fid:
        fid['features'] = clips

