# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound

import sqlite3 as sql
from flask import jsonify

database_name = "apps/app.db"

@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

def get_db_connection():
    conn = sql.connect(database_name)
    conn.row_factory = sql.Row
    return conn

@blueprint.route('/get_data')
def get_data():
    table = request.args.get('table')
    con = get_db_connection()
    cursor = con.cursor()
    data = None
    columns = []
    d = {}
    datas = []
    try:
        query = f"SELECT * FROM '{table}' ORDER BY id ASC LIMIT 10"
        # cursor.execute(query, (start_date, end_date))
        table = cursor.execute(query)

        # Fetch all the rows
        data = cursor.fetchall()
        cursor.close()

        for column in table.description: 
            columns.append(column[0])
        print(columns)
        # datas.append(columns)

        for row in data:
            # print(row)
            d = { columns[index]: x  for index, x in enumerate(row) }
            datas.append(d)
    except sql.Error as e:
        print("SQLite Error:", e)
    finally:
        con.close()
        print(datas)      
    return  jsonify(datas)
