from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import io
import os
import numpy as np
from string import ascii_lowercase
from werkzeug.utils import secure_filename
from pathlib import Path
from colour import colour


app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = Path('uploads')

# Ensure the upload folder exists
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file_path = app.config['UPLOAD_FOLDER'] / filename
        file.save(file_path)
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        return render_template('index.html', columns=columns, filename=filename)
    return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
def process():
    row_vars = request.form.getlist('row_vars')
    col_vars = request.form.getlist('col_vars')
    weight_var = request.form.get('weight_var')
    if weight_var == "":
        weight_var = None
    filename = request.form.get('filename')
    file_path = app.config['UPLOAD_FOLDER'] / filename
    output_file = 'TableOutputs{}.xlsx'.format(filename)
    df = pd.read_csv(file_path)
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    for i, row in enumerate(row_vars):
        finalframe = colour(df, rowname=row, listofcolnames=col_vars, weightvar=weight_var)
        finalframe.to_excel(writer, sheet_name=f'Table{i+1}')
    writer.close()
    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
