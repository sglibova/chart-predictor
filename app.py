from flask import Flask, flash, send_from_directory, render_template, request, redirect, url_for
from waitress import serve
from src.utils import extract_feature_values
from src.models.predictor import get_prediction
from werkzeug.utils import secure_filename
import pandas as pd
import os
from step_parser import batch_analysis


app = Flask(__name__, static_url_path="/static")
app.config['MAX_CONTENT_LENGTH'] = 2048000
app.secret_key = 'key'


@app.route("/")
def index():
    """Return the main page."""
    return send_from_directory("static", "index.html")


@app.route("/make_prediction", methods=['POST'])
def upload_predict():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for("index"))

        file = request.files['file']
        verifier = request.form['verifier']
        filename = secure_filename(file.filename)

        # if no file selected, browser submits an empty part without filename
        if filename and file.filename != '':
            data = batch_analysis(file)
            song_names = data['title']
            feature_values, stamina = extract_feature_values(data, verifier)
            print(data, verifier)  # debugging

            preds = get_prediction(feature_values, stamina)
            prediction = dict(zip(song_names, preds))

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

    # prediction = round(float(prediction), 2)

    # Return the results pge
    return render_template("results.html", prediction=prediction)


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
