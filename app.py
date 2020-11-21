import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitations for the past year"""
    # Query all precipitation list
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').all()

    session.close()

# Create a dictionary from the row data and append to a list of one year prcp
    one_year_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        one_year_prcp.append(prcp_dict)


    return jsonify(one_year_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of weather stations"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observation for the most active station in the last 1 year of data"""
    # Query all temperature observation
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-18').\
        order_by(Measurement.date.desc()).all()

    session.close()

 # Create a dictionary from the row data and append to a list of tobs_list
    tobs_list = []
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)


    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def timestart(start):
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of tobs_list
    time_list = []
    for result in results:
        time_dict = {}
        time_dict["date"] = result[0]
        time_dict["TMIN"] = result[1]
        time_dict["TMAX"] = result[2]
        time_dict["TAVG"] = result[3]
        time_list.append(time_dict)

    return jsonify(time_list)

@app.route("/api/v1.0/<start>/<end>")
def timerange(start, end):
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).\
        group_by(Measurement.date).all()
    session.close()

 # Create a dictionary from the row data and append to a list of tobs_list
    time_list = []
    for result in results:
        time_dict = {}
        time_dict["date"] = result[0]
        time_dict["TMIN"] = result[1]
        time_dict["TMAX"] = result[2]
        time_dict["TAVG"] = result[3]
        time_list.append(time_dict)

    return jsonify(time_list)



if __name__ == '__main__':
    app.run(debug=True)
