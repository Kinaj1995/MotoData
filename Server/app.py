from fileinput import filename
from flask import Flask, render_template, request, url_for

import os

UPLOAD_FOLDER = 'static/upload'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


## ================ WEBINTERFACE =================== ##
## 
##
## ================================================= ##

@app.route('/')
def index():
   return render_template('index.html')
	
   
@app.route('/', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      file = request.files['file']
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
      return render_template('index.html', file=filename)