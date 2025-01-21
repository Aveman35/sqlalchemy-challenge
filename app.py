# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
# Create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prec_results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    all_dates = []
    for date, prcp in prec_results:
        dates_dict = {}
        dates_dict["date"] = date
        dates_dict["prcp"] = prcp
        all_dates.append(dates_dict)

    return jsonify(all_dates)

# Create stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_results = session.query(Station.station, Station.name).all()
    session.close()

    #all_stations = list(np.ravel(station_results))
    all_stations = []
    for station, name in station_results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        all_stations.append(stations_dict)

    return jsonify(all_stations)

# Create tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent_date = dt.date(2017, 8, 23)
# Calculate the date one year from the last date in data set.
    one_year_ago = most_recent_date - dt.timedelta(days=365)
   
    #most_active_station = (
    #session.query(Station.station, func.count(Measurement.station))
    #.select_from(Station)
    #.outerjoin(Measurement, Station.station == Measurement.station)
    #.group_by(Station.station)
    #.order_by(func.count(Measurement.station).desc())
    #.first())
    
    most_active_station = session.query(
        Station.station, 
        func.count(Measurement.station).label('station_count')
    ).select_from(Station).outerjoin(Measurement, Station.station == Measurement.station).filter(
        Measurement.date >= one_year_ago
    ).group_by(Station.station).order_by(
        func.count(Measurement.station).desc()
    ).first()

    temperature_observations = session.query(
        Measurement.date, 
        Measurement.tobs
    ).filter(
        Measurement.station == most_active_station[0][0],
        Measurement.date >= dt.date(2016, 8, 23) #one_year_ago
    ).all()
        

    temp_results = [
        {"date": item.date.strftime('%Y-%m-%d'), "tobs": item.tobs}
        for item in temperature_observations]

    return jsonify(temp_results)




if __name__ == '__main__':
    app.run(debug=True)
