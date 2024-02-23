import bleach
import pandas as pd

from app import app
from app import db
from app.forms import  UploadForm, StoreForm
from flask import render_template, session, flash, redirect, url_for, request
import sqlite3
from datetime import datetime
from app.models import Dataset

sqlite_db = 'data.sqlite'


def store_data(df, table_name):
    conn = sqlite3.connect(sqlite_db)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()


# def get_db_tables():
#     conn = sqlite3.connect(sqlite_db)
#     cur = conn.cursor()
#     cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cur.fetchall()
#     conn.close()
#     return tables

def get_datasets():
    datasets = Dataset.query.all()
    dataset_list = []
    for dataset in datasets:
        dataset_info = {
            'id': dataset.id,
            'name': dataset.name,
            'date_added': dataset.date_added,
            'column_count': dataset.column_count,
            'columns': dataset.columns,
            'row_count': dataset.row_count,
            # If you want to include data, you can do so here
            # 'data': dataset.data
        }
        dataset_list.append(dataset_info)
    return dataset_list


@app.route('/')
def home():  # put application's code here
    return render_template('index.html')


@app.route('/manage')
def manage():
    datasets = get_datasets()
    if datasets:
        flash(f'There are {len(datasets)} datasets to manage.', category='success')
    else:
        flash('There are currently no datasets to manage. Upload and store a dataset.', 'warning')

    return render_template('manage.html', datasets=datasets)


@app.route('/data', methods=['GET', 'POST'])
def data():  # put application's code here
    flash('Free users can upload csv files only, max file size 100kb.', 'warning')
    csv_name = None
    upload_form = UploadForm()
    store_form = StoreForm()
    csv_df = None
    csv_html = None
    is_final_commit = False

    if store_form.validate_on_submit() and 'store' in request.form:
        data_json = session.get('data')
        data_name = session.get('data_name')
        if data_json:
            data_df = pd.read_json(data_json)
                # id = db.Column(db.Integer, primary_key=True)
            dataset = Dataset( name = data_name,
                              date_added = datetime.now(),
                              column_count = len(data_df.columns),
                              columns = ', '.join(data_df.columns),
                              row_count = len(data_df),
                              data = data_json)
            db.session.add(dataset)
            db.session.commit()
            # df = pd.read_json(data_json)

            # store_data(pd.read_json(data_json), data_name)

        is_final_commit = True
        flash('CSV stored, and available to Visualize or Manage.', 'success')

    elif store_form.validate_on_submit() and 'abort' in request.form:
        flash('File processing aborted.', 'danger')
    else:

        if upload_form.validate_on_submit():
            csv_name = upload_form.data_name.data

            csv_df = pd.read_csv(upload_form.csv_file.data, encoding='utf-8')

            # should break this out into a more robust custom converter on read_csv
            csv_df.map(lambda x: bleach.clean(x) if isinstance(x, str) else x)

            # stage this in a database for larger datasets, and where the preview steps
            # might include schema changes
            session['data'] = csv_df.to_json()
            session['data_name'] = csv_name

            csv_html = (csv_df.to_html(index=False
                                       , classes='table table-bordered table-striped'
                                       , table_id='data_table'))
            # data_sql = csv_to_pd.to_sql('data_table')
            upload_form.data_name.data = ''
            flash('CSV successfully uploaded.', 'success')

        elif upload_form.errors:
            flash('Invalid upload! csv files under 100kb only!', 'danger')

    return render_template('data.html'
                           , upload_form=upload_form
                           , store_form=store_form
                           , data_name=csv_name
                           , data_frame=csv_df
                           , table=csv_html
                           , is_final_commit=is_final_commit)


@app.route('/viz')
def viz():
    datasets = get_datasets()
    if datasets:
        flash(f'There are {len(datasets)} datasets to visualize.', category='success')
    else:
        flash('There are currently no datasets to visualize. Upload and store a dataset.', 'warning')

    return render_template('viz.html', datasets=datasets)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('na.html'), 404