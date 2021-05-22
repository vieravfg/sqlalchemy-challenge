import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


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
Station =  Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
# Home page. List all routes that are available.
#################################################

@app.route("/")
def welcome():
    print("Server received request for 'Home' page...")
    """List all available api routes."""
    return (
        f"Welcome to Hawaii!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
#################################################
# Convert the query results to a dictionary using 
# date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
#################################################

@app.route("/api/v1.0/precipitation")

def precipitation():
    # Create our session (link) from Python to the DB
    print("Server received request for 'precipitation' page")
    session = Session(engine)

    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= previous_year).all() 

    session.close()

    all_prcp = dict(results)
    
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")

def stations():
    # Create our session (link) from Python to the DB
    print("Server received request for 'stations' page")
    session = Session(engine)

    results = session.query(Measurement.station).\
    group_by(Measurement.station).all()

    session.close()
    #Convert list of tuples into normal list
    all_stations =  list(np.ravel(results)) 
    
    return jsonify(all_stations)


###########################################################
# Query the dates and temperature observations of the most 
# active station for the last year of data.
###########################################################
@app.route("/api/v1.0/tobs")

def tobs():
    print("Server received request for 'tobs' page")
    session = Session(engine)
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs, Measurement.date).\
    filter(Measurement.date >= previous_year).\
    filter(Measurement.station == 'USC00519281').all()

    session.close()

    # Create a dictonary of dates and tobs and append to a list of tobs_list
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

###########################################################
# Return a JSON list of the minimum temperature, the 
# average temperature, and the max temperature for a given 
# start or start-end range
###########################################################
@app.route("/api/v1.0/<start>")

def start(start):

    print("Server received request for 'start date' page")
    session = Session(engine)
    results = session.query(Measurement.date).all()
    
    all_startdates =  list(np.ravel(results))
    
    # Calculate TMIN, TAVG, and TMAX
    for sd in all_startdates:
        if sd == start:
            new_results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs), Measurement.date).\
            filter(Measurement.date >= start).group_by(Measurement.date).\
            order_by(Measurement.date).all()
        
            temp_list = []

            for min, max, avg, date in new_results:
                dict = {'Min Temp': min, 'Max Temp': max, 'Mean Temp': round(avg,2), 'Date': date} 
                temp_list.append(dict)
            return jsonify(temp_list)    
        
    session.close()
   
    return jsonify({"error": f" Date: {start} has not been not found."}), 404

###########################################################
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    print("Server received request for 'dates between start and end date' page")
    session = Session(engine)
    # Calculate TMIN, TAVG, and TMAX

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs), Measurement.date).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).\
    order_by(Measurement.date).all()
    
    temp_list = []
    for min, max, avg, date in results:
        dict = {'Min Temp': min, 'Max Temp': max, 'Mean Temp': round(avg,2), 'Date': date} 
        temp_list.append(dict)
    return jsonify(temp_list)    
        
    session.close()

    return jsonify(range)


if __name__ == '__main__':
    app.run(debug=True)
