#################################################
# Library Import
#################################################

from flask import Flask, jsonify

#%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Library Import
#################################################

from flask import Flask, jsonify


#################################################
# Reflect Tables into SQLAlchemy ORM
#################################################
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

Base = automap_base()
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


#################################################
# Flask Routes
#################################################
app = Flask(__name__)
@app.route("/")
def welcome():
    return (
        f"Welcome to climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Create a dictionary from the row data and append to precipitation list
    precipitation_list = []
    for date, prcp in prcp:
        prcp_result = {}
        prcp_result["date"] = date
        prcp_result["prcp"] = prcp
        precipitation_list.append(prcp_result)

    return jsonify(precipitation_list)


@app.route("/api/v1.0/stations")
def stations():
    station_count = session.query(Station.station).all()
    session.close()

    station_list = []

    for name in station_count:
        station_dict = {}
        station_dict["name"] = name
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    active_count = session.query(Measurement.station, func.count(Measurement.station) ).\
                group_by(Measurement.station).all()
    station_count_df = pd.DataFrame(active_count, columns = ["station","count"]).sort_values("count", ascending = False)
    most_active_station = station_count_df.iloc[0]["station"]
    session.close()

    active_count = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_station).\
                filter(Measurement.date > '2016-07-31' ).all()
    session.close()

    # Create a dictionary from the row data and append to precipitation list
    active_tobs = []
    for date, tobs in active_count:
        tobs_result = {}
        tobs_result["date"] = date
        tobs_result["tobs"] = tobs
        active_tobs.append(tobs_result)

    return jsonify(active_tobs)

@app.route("/api/v1.0/<start_date>")
def temp_start(start_date):
    calc = session.query(Measurement.date, func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs) ).\
        filter(Measurement.date >= start_date).all()
    session.close()

    active_tobs = []
    for date, min_tobs, avg_tobs, max_tobs in calc:
        start_obs = {}
        start_obs["date"] = date
        start_obs["min_tobs"] = min_tobs
        start_obs["avg_tobs"] = avg_tobs
        start_obs["max_tobs"] = max_tobs
        active_tobs.append(start_obs)

    return jsonify(active_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def combined_start(start_date,end_date):
    calc = session.query(Measurement.date, func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs) ).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    combined_tobs = []
    for date, min_tobs, avg_tobs, max_tobs in calc:
        combined_obs = {}
        combined_obs["date"] = date
        combined_obs["min_tobs"] = min_tobs
        combined_obs["avg_tobs"] = avg_tobs
        combined_obs["max_tobs"] = max_tobs
        combined_tobs.append(combined_obs)

    return jsonify(combined_tobs)

if __name__ == "__main__":
    app.run(debug=True)
