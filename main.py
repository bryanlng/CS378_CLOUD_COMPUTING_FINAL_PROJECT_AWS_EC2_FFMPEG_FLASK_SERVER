import os
import time

from flask import request
from flask import Flask, render_template

application = Flask(__name__)
app = application

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/convert_video", methods = ['GET'])
def convert_video():
	url = request.args.get("url")
	desired_format = request.args.get("desired_format")



if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
