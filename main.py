from flask import Flask, render_template, request, flash, redirect, url_for  # noqa : E501
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
import os
from flask_session import Session
from pathlib import Path
# import grader


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.secret_key = "k2s04isthebestcompoundnameihaveeverheardinmahlife"
app.config["SESSION_PERMANENT"] = False
app.config['DEBUG'] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

UPLOAD_FOLDER = 'data'


def allowed_file(filename):
    file_format = filename.split(".")[1]
    if file_format == "jpg":
        return True
    return False


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route("/process", methods=['GET', 'POST'])
def process():

    if request.method == 'POST':

        # check if the size of the file is within limit
        try:
            if 'file' not in request.files:
                flash('No file part')
                return redirect(url_for('home'))
            file = request.files['file']
        except RequestEntityTooLarge:
            flash("Too Large")
            return redirect(url_for('home'))

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No File Selected')
            return redirect(url_for('home'))

        # if file exists and the format is mp4 then firstly we secure
        # the filename. Then save the file to upload folder
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = os.path.join(
                UPLOAD_FOLDER, filename).replace("\\", "/")

            Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
            file.save(file_path)
#             grader.grade(file_path)
            return redirect(url_for('complete'))

        flash("The File Format Must be JPG")
        return redirect(url_for('home'))


@app.route('/complete')
def complete():
    return render_template('complete.html')


if __name__ == '__main__':
    app.run()
