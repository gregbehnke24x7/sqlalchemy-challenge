import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

#inspector = inspect(engine)
#table_names = inspector.get_table_names()
#print(table_names)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    # List available routes.
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"Append single date to string above in 'YYYY-MM-DD/YYYY-MM-DD' format<br/>"        
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Append start and end dates to string above in 'YYYY-MM-DD/YYYY-MM-DD' format<br/>"
    )


@app.route("/api/v1.0/precipitation")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prior_year_prcp = session.query(Measurements.station, Measurements.date, Measurements.prcp).filter(Measurements.date >= year_prior).all()#

    session.close()##

    # Create a dictionary from the data and append to a list of precipitation recordings
    precip = []
    for date, station, prcp in prior_year_prcp:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["station"] = station
        precip_dict["prcp"] = prcp
        precip.append(precip_dict)


    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a list of all weather monitoring stations
    results = session.query(Stations.station, Stations.name).all()

    session.close()

    # Create a dictionary from the row data and append to a list of stations
    all_stations = []
    for station in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def active_temps():
   # Create our session (link) from Python to the DB
    session = Session(engine)

   # Return a list of all weather monitoring stations with the count of observations for each
    results = session.query(Measurements.station, func.count(Measurements.station))\
             .group_by(Measurements.station).all()

    station_counts = []
    for station in results:
        station_dict = {}
        station_dict["station"] = station[0]
        station_dict["count"] = station[1]
        station_counts.append(station_dict)

    sorted_counts = sorted(station_counts, reverse=True, key = lambda i: i['count'])
    active = sorted_counts[0]
    active_station = active['station']
   # Return a list of all temp observations for the most active station
    results = session.query(Measurements.station, Measurements.date, Measurements.tobs).filter(Measurements.station == active_station).all()

    session.close()

    station_temps = []
    for reading in results:
        reading_dict = {}
        reading_dict["station"] = reading[0]
        reading_dict["date"] = reading[1]
        reading_dict["observed"] = reading[2]
        station_temps.append(reading_dict)

    return jsonify(station_temps)


@app.route("/api/v1.0/<start>")
def date_temps(start):
   # Create our session (link) from Python to the DB
    session = Session(engine)

    # When start only is supplied, calculate tobs min, max, and average for all dates GE to the start date
    results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
              filter(Measurements.date >= start).order_by(Measurements.date.desc()).all()

    session.close()

    for stat in results:
        stat_dict = {
             "minimum reading" : results[0][0],
             "average reading" : results[0][1],
             "maximum reading" : results[0][2] 
        }
    
    return jsonify(stat_dict) 


@app.route("/api/v1.0/<start>/<end>")
def date_range_temps(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # If start and end date are supplied, calculate tobs min, max, and average for all dates GE to the start date
    # and LE to the end date
    results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs),func.max(Measurements.tobs)).\
                  filter(Measurements.date >= start, Measurements.date <= end).order_by(Measurements.date.desc()).all()

    session.close()

    for stat in results:
        stat_dict = {
             "minimum reading" : results[0][0],
             "average reading" : results[0][1],
             "maximum reading" : results[0][2] 
        }
    
    return jsonify(stat_dict) 

if __name__ == '__main__':
    app.run(debug=True)
