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

    return render_template('home/messages.html', segment='index')


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
        query = f"SELECT * FROM '{table}' ORDER BY id ASC LIMIT 30"
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
            try:
                del d['document']
            except:
                pass
            datas.append(d)
    except sql.Error as e:
        print("SQLite Error:", e)
    finally:
        con.close()
        print(datas)      
    return  jsonify(datas)

@blueprint.route('/update_datas', methods=['GET', 'POST'])
def update_data():
    if request.method == 'POST':
        try:
            # Retrieve the updated data from the POST request as JSON
            updated_data = request.get_json()
            print('POST request', updated_data)
            # Extract the relevant data from the JSON request
            table = request.args.get('table')
            record_id = updated_data.get('ID')
            del updated_data['ID']

            # Update the "messages" table in the database
            con = sql.connect(database_name)
            cur = con.cursor()
            # Generate the SET clause for the SQL query
            set_clause = ", ".join(f"{key} = ?" for key in updated_data.keys())
            # Create a list of values to update
            values_to_update = list(updated_data.values())

            # Use an SQL UPDATE statement to update the "status" and "sent" columns
            update_query = f"UPDATE '{table}' SET {set_clause} WHERE ID = {record_id}"
            print(update_query)
            cur.execute(update_query, values_to_update)
            con.commit()
            con.close()

            response_data = {'messages': 'Data updated successfully'}
            return jsonify(response_data), 200  # Respond with JSON and HTTP status code 200 (OK)

        except Exception as e:
            error_message = {'error': str(e)}
            print(e)
            return jsonify(error_message), 500  # Respond with an error and HTTP status code 500 (Internal Server Error)

    # Handle invalid requests or other conditions here
    return jsonify({'error': 'Invalid request'}), 400  # Respond with an error and HTTP status code 400 (Bad Request)