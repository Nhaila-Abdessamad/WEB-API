from flask import Flask, request, render_template
import json
import plotly
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
#from sqlalchemy import create_engine
import psycopg2
import psycopg2.extras as extras
import os

CREATE_ROOMS_TABLE = (
    "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);"
)

CREATE_TEMPS_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL, 
                        date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""

INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"

INSERT_TEMP = (
    "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"
)

ROOM_NAME = """SELECT name FROM rooms WHERE id = (%s)"""

ROOM_NUMBER_OF_DAYS = """SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures WHERE room_id = (%s);"""

ROOM_ALL_TIME_AVG = (
    "SELECT AVG(temperature) as average FROM temperatures WHERE room_id = (%s);"
)

ROOM_TERM = """SELECT DATE(temperatures.date) as reading_date,
AVG(temperatures.temperature)
FROM temperatures
WHERE temperatures.room_id = (%s)
GROUP BY reading_date
HAVING DATE(temperatures.date) > (SELECT MAX(DATE(temperatures.date))-(%s) FROM temperatures);"""

GLOBAL_NUMBER_OF_DAYS = (
    """SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"""
)
GLOBAL_AVG = """SELECT AVG(temperature) as average FROM temperatures;"""

CREATE_TABLE_US = '''CREATE TABLE us_fruits(Fruit char(20) ,Amount
INTEGER ,City char(20));'''

CREATE_TABLE_EU = '''CREATE TABLE eu_vegs(Vegetables char(20) ,Amount
INTEGER ,City char(20));'''

ROOM_TABLE = "select * from rooms"

EU_VEGs_TABLE = "select * from eu_vegs"

US_FRUITS_TABLE = "select * from us_fruits"

FLASK_APP= "app.py"
FLASK_DEBUG= 1


url = "postgres://rtmntofy:iA-Z9YumhZ5hjjdul_vcUmov7v63HVsD@mouse.db.elephantsql.com/rtmntofy"
connection = psycopg2.connect(url)
#engine = create_engine(url)
app = Flask(__name__)


def execute_values(conn, df, table):
  
    tuples = [tuple(x) for x in df.to_numpy()]
  
    cols = ','.join(list(df.columns))
  
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("execute_values() done")
    cursor.close()


def create_table(query):
    cursor = connection.cursor()
    cursor.execute(query)
    print("table created")

# execute_values(connection, data, 'us_fruits')

#create_table(CREATE_TABLE_EU)

#execute_values(connection, data, 'eu_vegs')

def get_df(table_query):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(table_query)
            data = cursor.fetchall()
            cols = []
            for elt in cursor.description:
                cols.append(elt[0])   
            df=pd.DataFrame(data=data,columns=cols)
    return df



@app.route('/')
def chart():
    # Graph 0
    df0 =get_df(EU_VEGs_TABLE) 
    fig0 = go.Figure(data=[go.Table(
    header=dict(values=list(df0.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df0.vegetables, df0.amount, df0.city],
               fill_color='lavender',
               align='left'))
    ])
    graph0JSON = json.dumps(fig0, cls=plotly.utils.PlotlyJSONEncoder)

    # Graph One
    df = px.data.medals_wide()
    fig1 = px.bar(df, x="nation", y=["gold", "silver", "bronze"], title="Wide-Form Input")
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    # Graph two
    df = px.data.iris()
    fig2 = px.scatter_3d(df, x='sepal_length', y='sepal_width', z='petal_width',
              color='species',  title="Iris Dataset")
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # Graph three
    df = px.data.gapminder().query("continent=='Oceania'")
    fig3 = px.line(df, x="year", y="lifeExp", color='country',  title="Life Expectancy")
    graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    # Graph 4
    df =get_df(EU_VEGs_TABLE) 
    fig = px.box(df, y="amount")
    graph4JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', graph0JSON=graph0JSON,  graph1JSON=graph1JSON,  graph2JSON=graph2JSON, graph3JSON=graph3JSON, graph4JSON=graph4JSON)