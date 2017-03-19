""" s3_and_hdf5.py

Generate hdf5 files with clips from data in s3

In s3 I have a bucket called "geometrical-images", inside that bucket I have lots of
clips under different prefixes. Currently the only prefix is "rotation" which has keys
00000.pkl to 00001.pkl, etc

Load those images and generate an hdf5 from them
"""
import boto3
import h5py
import tempfile
import _pickle as pickle

from clips import config

AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
UNITY_ASSETS = config.UNITY_ASSETS
S3_PREFIX = config.S3_PREFIX
BUCKET = config.BUCKET

def main(prefix):
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    paginator = client.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=BUCKET, Prefix=prefix)

    _, temp_pkl = tempfile.mkstemp(suffix='.pkl')
    print(temp_pkl)

    # for the time being there is only one label, but if this works I'll have more soon
    labels = []
    features = []
    for page in page_iterator:
        for item in page['Contents']:
            key = item['Key']
            print(key)
            client.download_file(BUCKET, key, temp_pkl)

            fid = open(temp_pkl, 'rb')
            clip = pickle.load(fid)

            labels.append(0)
            features.append(clip)

            if len(labels) >= 5:
                break

        break

    # store all features/labels in a temp hdf5
    _, temp_h5py = tempfile.mkstemp(suffix='.hdf5')
    with h5py.File(temp_h5py) as fid:
        fid['features'] = features
        fid['labels'] = labels

    # upload to s3
    client.upload_file(temp_h5py, BUCKET, 'clips.hdf5')


if __name__ == "__main__":
    prefix = 'rotation'
    main(prefix)
