from fileinput import filename
from importlib.metadata import files
from flask import Flask, render_template, request, url_for, abort, send_file

import os

UPLOAD_FOLDER = 'static/upload'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


## ================ WEBINTERFACE =================== ##
##
##
## ================================================= ##


## ================ UPLOAD FILE =================== ##

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], file.filename)):
            return 'A File with the same name already exists. Please choose another Filename.'

        else:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return render_template('index.html', file=filename)


## ================ LIST FILES =================== ##

def dir_listing():
    
    # Show directory contents
    files = os.listdir(UPLOAD_FOLDER)
    return files


## ================ TEMPLATES =================== ##

@app.route('/')
def index():    
    return render_template('index.html', files=dir_listing())



## ================ START SERVER =================== ##
if(__name__ == "__main__"):
   app.run(debug=True, host="127.0.0.1")  # Server startparameter  
