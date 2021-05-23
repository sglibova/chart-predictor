from flask import Flask, flash, send_from_directory, render_template,\
     request, redirect, url_for
from waitress import serve
from src.utils import allowed_file, extract_feature_values
from src.models.predictor import get_prediction
from werkzeug.utils import secure_filename
import os
import re
from step_parser import batch_analysis

import warnings
warnings.filterwarnings("ignore")


app = Flask(__name__, static_url_path="/static")

app.secret_key = 'key'

# max file size
app.config['MAX_CONTENT_LENGTH'] = 2048000

# file upload path
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')

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

    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    # if the folder isn't empty, this will remove any excess files from it
    for oldfile in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, oldfile)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    files = request.files.getlist('files[]')

    # upload files to 'uploads' folder
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

    # user input of stamina or tech
    verifier = request.form['verifier']

    # run sm_tools batch_analysis to generate a dataframe of song features
    data = batch_analysis(UPLOAD_FOLDER)
    song_name = data['title']
    difficulty = data['difficulty']

    feature_values, stamina = extract_feature_values(data, verifier)

    prediction = get_prediction(feature_values, stamina)

    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.remove(file_path)

    return redirect(url_for("show_results", song_name=song_name,
                            difficulty=difficulty, prediction=prediction))


@app.route("/show_results")
def show_results():
    """ Display the results page with the provided prediction """

    # Extract the names, difficulties, and predictions from the URL params
    # string formatting
    song_name = request.args.get("song_name").split('Name')[0]
    song_list = re.findall('[A-Z]\w+\d*\D+', song_name)
    
    # string formatting
    difficulty = request.args.get("difficulty").split('Name')[0]
    difficulty_list = re.findall('[A-Z]\w+\d*\D+', difficulty)

    # string formatting
    prediction = request.args.get("prediction").strip('[]')
    prediction_list = prediction.split()

    # remove uploads directory
    filenames = os.listdir(UPLOAD_FOLDER)
    if len(filenames) != 0:
        for filename in filenames:
            if os.path.isfile(filename):
                os.remove(filename)

    os.rmdir(UPLOAD_FOLDER)

    # Return the results pge
    return render_template("results.html", song_list=song_list,
                           difficulty_list=difficulty_list,
                           prediction_list=prediction_list)


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
