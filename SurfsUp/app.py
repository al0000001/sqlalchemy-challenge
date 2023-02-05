import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save reference to the table
Measurement = Base.classes.measurement
Station= Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
        return (
        f"Welcome to the trip plan website" 
        f"Available Routes:<br/>"       
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/Start<br/>"
        f"Searching format example: http://127.0.0.1:5000/api/v1.0/startdateyyyy-mm-dd<br/>"
        f"/api/v1.0/Start/End<br/>"
        f"Searching format example: http://127.0.0.1:5000/api/v1.0/startdate yyyy-mm-dd/enddate yyyy-mm-dd/<br/>"
        f"Searching format example: http://127.0.0.1:5000/api/v1.0/2017-01-01<br/>"
        f"Searching format example: http://127.0.0.1:5000/api/v1.0/2017-01-01/2018-08-21"
    )

#----------------------------------------

@app.route("/api/v1.0/precipitation")
def passengers():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    result_p = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of prcp
    date_prcp = []
    for date, prcp in result_p:
        date_prcp_dict = {}
        date_prcp_dict["Date"] = date
        date_prcp_dict["Prcp"] = prcp

        date_prcp.append(date_prcp_dict)

    return jsonify(date_prcp)




@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station"""
    # Query all station
    result_s = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_station = list(np.ravel(result_s))

    return jsonify(all_station)

#Method copied and learnt from https://github.com/MThorpester/sqlalchemy-challenge/blob/main/app.py
#Detail code has adjusted to suit for this case

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the last 12 months of temperature observation data for the most active station
    # Date was found via below:
    #Step 1session.query(MEASUREMENT.date).order_by(MEASUREMENT.date.desc()).first()
    #Step 2year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    #Step 3prcp_query_result=session.query(MEASUREMENT.date, MEASUREMENT.prcp).filter(MEASUREMENT.date >= year_ago).all()
    #Step 4Save the query results as a Pandas DataFrame and set the index to the date column

    start_date = '2016-08-23'
    sel = [Measurement.date, 
        Measurement.tobs]
    station_info = session.query(*sel).\
            filter(Measurement.date >= start_date, Measurement.station == 'USC00519281').\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()

    session.close()

    # Return a dictionary with the date as key and the daily temperature observation as value
    key_dates = []
    key_temperature = []

    for kd, kt in station_info:
        key_dates.append(kd)
        key_temperature.append(kt)
    
    most_active_station_info= dict(zip(key_dates, key_temperature))

    return jsonify(most_active_station_info)

#Method copied and learnt from https://github.com/MThorpester/sqlalchemy-challenge/blob/main/app.py
#Detail code has adjusted to suit for this case

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_result = session.query(func.min(Measurement.tobs), \
                func.avg(Measurement.tobs),\
                func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    session.close()

    # Create a list stroge start_result dictories [list of dictionary]
    start_result_list = []
    for min,avg,max in start_result:
        start_result_dict = {}
        start_result_dict["Minimum Temperature"] = min
        start_result_dict["Average Temperature"] = avg
        start_result_dict["Maximum Temperature"] = max

        start_result_list.append(start_result_dict)

    return jsonify(start_result_list)

#Method copied and learnt from https://github.com/MThorpester/sqlalchemy-challenge/blob/main/app.py
#Detail code has adjusted to suit for this case
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_result = session.query(func.min(Measurement.tobs), \
                func.avg(Measurement.tobs),\
                func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

    session.close()

    # Create a list stroge start_result dictories [list of dictionary]
    start_end_result_list = []
    for min,avg,max in start_result:
        start_end_result_dict = {}
        start_end_result_dict["Minimum Temperature"] = min
        start_end_result_dict["Average Temperature"] = avg
        start_end_result_dict["Maximum Temperature"] = max

        start_end_result_list.append(start_end_result_dict)

    return jsonify(start_end_result_list)


if __name__ == '__main__':
    app.run(debug=True)
