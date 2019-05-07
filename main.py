import os
import time

from flask import request
from flask import Flask, render_template

from google.cloud import storage

application = Flask(__name__)
app = application



@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/convert_video", methods = ['GET'])
def convert_video():
	info = {}
	try:
		url = request.args.get("url")
		desired_format = request.args.get("desired_format")
		info["url"] = url
		info["desired_format"] = desired_format
	except Exception as e:
        	info["problems_just_e"] = str(e)
	return info


"""
Downloads it, in FILE form
"""
def download_object(source_blob_name, bucket_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))


"""
Uploads an object to the bucket
"""
def upload_object(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to bucket {} with dest filename{}.'.format(
        source_file_name, bucket_name,
        destination_blob_name))

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
