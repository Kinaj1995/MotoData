from fileinput import filename
from flask import Flask, render_template, request, url_for

import os

UPLOAD_FOLDER = 'static/upload'

app = Flask(__name__, template_folder='templates')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


## ================ WEBINTERFACE =================== ##
## 
##
## ================================================= ##

@app.route('/')
@app.route('/home')
def index():
   return render_template('index.html')
	
   
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
      return render_template('map.html')
		
if __name__ == '__main__':
   app.run(debug = True)