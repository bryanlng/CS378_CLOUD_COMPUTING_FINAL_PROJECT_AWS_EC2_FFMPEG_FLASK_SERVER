import os
import time
from flask import jsonify

from flask import request
from flask import Flask, render_template

from google.cloud import storage
import ffmpy
import ffmpeg
from urllib.parse import urlparse
import subprocess
from subprocess import Popen, run, PIPE, check_call, CalledProcessError, check_output

application = Flask(__name__)
app = application



@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/convert_video", methods = ['GET'])
def convert_video():
    """
    Calls FFMPEG

    Requires the following params:
    1. url
    2. desired_format

    Input:
    request object, which is a Flask Request object
    Extract the following parameters out from request.args:
    1. url:
        -the full url, not just the video id
        -we'll use this to create the bucket filename
        -format: <video_id>::<title>.mp4

    2. desired_format:
        -choices:
            -mp3, aac, flac, avi, mov, mkv

    Ex:
    https://us-central1-cs378-final-project-media.cloudfunctions.net/convert_video_cloud_function?url=https://www.youtube.com/watch?v=BotpJkJ0BKE&desired_format=mkv
    """
    url = str(request.args.get("url"))
    desired_format = str(request.args.get("desired_format"))

    info = {}
    try:
        #Create filename
        video_id = extract_video_id(url)
        filename = video_id + ".mp4"

        source_bucket_name = "cs378_final_raw_videos"
        dest_bucket_name = "cs378_final_converted_videos"
        info["source_bucket_name"] = source_bucket_name
        info["dest_bucket_name"] = dest_bucket_name
        info["filename"] = filename
        info["desired_format"] = desired_format


        if desired_format == "mp4":
            #It's already in mp4, so we don't have to convert it. Make a copy of it and move it to the converted bucket
            # copy_and_write_object(source_bucket_name, filename, dest_bucket_name)
            print("copy_and_write_object")
        else:
            #Get file from raw bucket
            # download_object(filename, source_bucket_name, "/tmp/" + filename)

            filename_in_tmp = ""
            files_in_tmp = "Files: "
            dirs_in_tmp = " Dirs: "
            for root, dirs, files in os.walk("/tmp"):
                for filename in files:
                    filename_in_tmp += str(os.path.join(root, filename))
                    files_in_tmp += str(os.path.join(root, filename)) + ", "
                for dirname in dirs:
                    dirs_in_tmp += str(os.path.join(root, dirname))
            info["before_files_and_dirs_in_tmp"] = files_in_tmp + dirs_in_tmp
            info["filename_in_tmp"] = filename_in_tmp
            output_filename = filename[:len(filename)-len(desired_format)] + desired_format
            info["output_filename"] = output_filename

            #Run the ffmpeg command using the os.popen command
            # p = subprocess.run('sudo apt-get install ppa-purge && sudo ppa-purge ppa:jonathonf/ffmpeg-4', stdout=PIPE, input='\n', shell=True, encoding='ascii')
            # info["Pass -1: idempotent sudo apt-get install ppa-purge && sudo ppa-purge ppa:jonathonf/ffmpeg-4"] = "yes"
            #
            # p = subprocess.run('sudo add-apt-repository ppa:jonathonf/ffmpeg-4', stdout=PIPE, input='\n', shell=True, encoding='ascii')
            # info["Pass 0: sudo add-apt-repository ppa:jonathonf/ffmpeg-4"] = "yes"
            #
            # p = subprocess.run('sudo apt-get update', stdout=PIPE, input='\n', shell=True, encoding='ascii')
            # info["Pass 1: sudo apt-get update"] = "yes"
            #
            # p = subprocess.run('sudo apt-get install ffmpeg', stdout=PIPE, input='\n', shell=True, encoding='ascii')
            # info["Pass 2: sudo apt-get install ffmpeg"] = "yes"
            #
            # p = subprocess.run('sudo apt-get install frei0r-plugins', stdout=PIPE, input='\n', shell=True, encoding='ascii')
            # info["Pass 3: sudo apt-get install frei0r-plugins"] = "yes"
            #
            # p = subprocess.check_output("ffmpeg -version", shell=True, encoding='ascii')
            # info["Pass 4: ffmpeg -version"] = str(p)

            # stream = ffmpeg.input(filename)
            # stream = ffmpeg.output(stream, output_filename)
            # ffmpeg.run(stream)

            # ff = ffmpy.FFmpeg(
            #     inputs={filename: None},
            #     outputs={output_filename: None}
            # )
            # ff.run()

            # cmd = 'ffmpeg -i ' + str(filename) + ' ' + str(output_filename)
            # p = subprocess.run(cmd,  shell=True, encoding='ascii', capture_output=True, check=True)
            # p = subprocess.check_call('ffmpeg -i ' + str(filename) + ' ' + str(output_filename), stdout=PIPE, input='\n', shell=True, encoding='ascii', capture_output=True, check=True)
            info["Pass 5: ffmpeg -i filename output_filename"] = "yes"

            files_in_tmp = "Files: "
            dirs_in_tmp = " Dirs: "
            for root, dirs, files in os.walk("/tmp"):
                for filename in files:
                    files_in_tmp += str(os.path.join(root, filename)) + ", "
                for dirname in dirs:
                    dirs_in_tmp += str(os.path.join(root, dirname)) + ", "
            info["after_files_and_dirs_in_tmp"] = files_in_tmp + dirs_in_tmp

            output_filename_new_format_in_tmp = filename_in_tmp[:len(filename_in_tmp)-len(desired_format)] + desired_format
            info["output_filename_new_format_in_tmp"] = output_filename_new_format_in_tmp

            #Upload to the "converted" Google Cloud Bucket
            # upload_object(dest_bucket_name, output_filename_new_format_in_tmp, output_filename)

    except CalledProcessError as cpe:
        info["CalledProcessError main output"] = str(cpe)
        info["CalledProcessError returncode"] = str(cpe.returncode)
        info["CalledProcessError cmd"] = str(cpe.cmd)
        info["CalledProcessError output"] = str(cpe.output)
    except Exception as e:
        info["problems_just_e"] = str(e)

    return jsonify(info)



"""
Extracts the video id out of the url
Takes in a URL in the form of a string
"""
def extract_video_id(url):
    youtube_share_urls = ["youtu.be", "www.youtu.be"]
    youtube_reg_urls = ["www.youtube.com", "youtube.com"]
    data = urlparse(url)
    hostname = str(data.hostname).lower()

    video_id = ""
    if hostname in youtube_share_urls:
        video_id = str(data.path)[1:]       #ex: /URNN-_az-3g
    else:
        parts = str(data.query).split("&")  #ex: v=URNN-_az-3g&t=40
        for part in parts:
            if part[0:2] == "v=":
                video_id = part[2:]
    return video_id


"""
Copies an object, then puts it into the destination_bucket
"""
def copy_and_write_object(source_bucket_name, blob_name, dest_bucket_name):
    """Copies a blob from one bucket to another with a new name."""
    storage_client = storage.Client()
    source_bucket = storage_client.get_bucket(source_bucket_name)
    source_blob = source_bucket.blob(blob_name)
    destination_bucket = storage_client.get_bucket(dest_bucket_name)

    new_blob = source_bucket.copy_blob(
        source_blob, destination_bucket, blob_name)

    print('Blob {} in source bucket {} copied to blob {} in dest bucket {}.'.format(
        source_blob.name, source_bucket.name, new_blob.name,
        destination_bucket.name))


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
