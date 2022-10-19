from fileinput import filename
from importlib.metadata import files
from site import abs_paths
from flask import Flask, render_template, request, url_for, abort, send_file, redirect

import os

UPLOAD_FOLDER = 'static/upload'

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


## ================ TEMPLATES =================== ##

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', files=dir_listing())


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




## ================ START SERVER =================== ##
if (__name__ == "__main__"):
    app.run(debug=True, host="127.0.0.1")  # Server startparameter
