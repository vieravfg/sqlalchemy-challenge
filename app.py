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
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")

def precipitation():
    # Create our session (link) from Python to the DB
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
    session = Session(engine)

    results = session.query(Measurement.station).\
    group_by(Measurement.station).all()

    session.close()
    all_stations =  list(np.ravel(results)) 
    
    return jsonify(all_stations)

if __name__ == '__main__':
    app.run(debug=True)