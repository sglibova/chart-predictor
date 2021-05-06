from flask import Flask, flash, send_from_directory, render_template, request, redirect, url_for
from flask_dropzone import Dropzone
from waitress import serve
from src.utils import allowed_file, extract_feature_values
from src.models.predictor import get_prediction
from werkzeug.utils import secure_filename
import pandas as pd
import os
from step_parser import batch_analysis


app = Flask(__name__, static_url_path="/static")

app.secret_key = 'key'
app.config['MAX_CONTENT_LENGTH'] = 2048000

#file upload path
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    """Return the main page."""
    return send_from_directory("static", "index.html")


@app.route("/make_prediction", methods=['POST'])
def upload_predict():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(url_for("index"))

        files = request.files.getlist('files[]')

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)


        verifier = request.form['verifier']
        

        # if no file selected, browser submits an empty part without filename
        if filename:
            data = batch_analysis(UPLOAD_FOLDER)
            print(data.columns)
            print(len(data))
            song_names = data['title']
            feature_values, stamina = extract_feature_values(data, verifier)

            preds = get_prediction(feature_values, stamina)
            prediction = dict(zip(song_names, preds))

            for file in files:
                name = "_".join(file.filename.split())
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], name)
                os.remove(file_path)

            return redirect(url_for("show_results", prediction=prediction))

        else:
            flash('No file selected! Try again.')
            return redirect(url_for("index"))


@app.route("/show_results")
def show_results():
    """ Display the results page with the provided prediction """

    # Extract the prediction from the URL params
    prediction = request.args.get("prediction")
    song_names = request.args.get("song_names")

    #remove uploads directory
    os.rmdir(UPLOAD_FOLDER)

    # Return the results pge
    return render_template("results.html", prediction=prediction)


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
