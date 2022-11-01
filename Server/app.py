from crypt import methods
from fileinput import filename
from importlib.metadata import files
from site import abs_paths
from flask import Flask, render_template, request, url_for, abort, send_file, redirect

import os
import csv

UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = {'csv'}

MAPSETTINGS = {"settings": [],
                "disableinput": False,
                "colorcount": 0,
                "colors": [
                    ["Red", "e85141", False],
                    ["Green","2ecc71", False],
                    ["Blue","abcdef", False]
                    ]
                }



app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


## ================ WEBINTERFACE =================== ##
##
##
## ================================================= ##


## ================ LIST FILES =================== ##

def dir_listing():
    # Show directory contents
    files = sorted(os.listdir(UPLOAD_FOLDER))
    return files

## ================ CHECK FILE Extentions =================== ##

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

        if(fname):
            datapath = os.path.join(app.config['UPLOAD_FOLDER'], fname + ".csv")
        else:
            datapath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        if os.path.isfile(datapath):
            return 'A File with the same name already exists. Please choose another Filename.'

        if file and allowed_file(file.filename):
            
            file.save(datapath)
            return redirect(url_for('index'))
        
        else:
            print('unsupported File')
            return redirect(url_for('index'))



@app.route('/resetsettings', methods=['GET'])
def resetSettings():

    global MAPSETTINGS


    MAPSETTINGS.clear()
    MAPSETTINGS = {"settings": [],
                "disableinput": False,
                "colorcount": 0,
                "colors": [
                    ["Red", "e85141", False],
                    ["Green","2ecc71", False],
                    ["Blue","abcdef", False]
                    ]
                }

    return redirect(url_for('index'))



@app.route('/selectfile', methods=['POST'])
def selectFile():

    global MAPSETTINGS


    data = request.form

    color = ""
    filename = data["filename"]

    print(data['flexRadio'])

    if ('flexRadio' in data):
        color = data['flexRadio']

        for c in MAPSETTINGS["colors"]:
            if(color in c):
                c[2] = True
                MAPSETTINGS["colorcount"] += 1

    else:
        print("No color found")
        color = "e85141" # Set default color






    MAPSETTINGS["settings"].append({"filename": filename, "color" : color})

    print(MAPSETTINGS)


    return redirect(url_for('index'))

@app.route('/deletfile', methods=['POST'])
def deleteFile():

    data = request.form

    if("filename" in data):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], data['filename']))

    return redirect(url_for('index'))

@app.route('/gauge')
def gauge():
    return render_template('gauge.html')



## ================ START SERVER =================== ##
if (__name__ == "__main__"):
    app.run(debug=True, host="127.0.0.1")  # Server startparameter
