from crypt import methods
from fileinput import filename
from importlib.metadata import files
from site import abs_paths
from flask import Flask, render_template, request, url_for, abort, send_file, redirect

import os
import csv

UPLOAD_FOLDER = 'static/upload'


MAPSETTINGS = {"settings": []}


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


## ================ WEBINTERFACE =================== ##
##
##
## ================================================= ##


## ================ LIST FILES =================== ##

def dir_listing():
    # Show directory contents
    files = os.listdir(UPLOAD_FOLDER)
    return files

"""
def set_marker(fname):
    results = []
    with open(UPLOAD_FOLDER + fname) as csvfile:
        # change contents to floats
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:  # each row is a list
            results.append(row)
"""

## ================ TEMPLATES =================== ##

@app.route('/', methods=['GET', 'POST'])
def index():
    global MAPSETTINGS
    if request.method == 'GET':
        return render_template('index.html', dirlist=dir_listing(), file="00013.csv", mapsettings=MAPSETTINGS)


@app.route('/upload_data', methods=['POST'])
def upload_data():

    if request.method == 'POST':
        file = request.files['file']
        fname = request.form['fname']
        abs_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)

        if os.path.isfile(abs_path + ".csv"):
            return 'A File with the same name already exists. Please choose another Filename.'

        else:
            file.save(abs_path + ".csv")
            return redirect(url_for('index'))



@app.route('/resetsettings', methods=['GET'])
def resetSettings():

    global MAPSETTINGS
    MAPSETTINGS.clear()
    MAPSETTINGS = {"settings": []}

    return redirect(url_for('index'))



@app.route('/selectfile', methods=['POST'])
def selectFile():

    global MAPSETTINGS

    data = request.form

    color = ""
    filename = data["filename"]

    if ('flexRadioRed' in data):
        print("Red")
        color = "e85141"
    if ('flexRadioGreen' in data):
        print("Green")
        color = "2ecc71"
    if ('flexRadioBlue' in data):
        print("Blue")
        color = "abcdef"


    MAPSETTINGS["settings"].append({"filename": filename, "color" : color})

    print(MAPSETTINGS)


    return redirect(url_for('index'))



@app.route('/gauge')
def gauge():
    return render_template('gauge.html')



## ================ START SERVER =================== ##
if (__name__ == "__main__"):
    app.run(debug=True, host="127.0.0.1")  # Server startparameter
