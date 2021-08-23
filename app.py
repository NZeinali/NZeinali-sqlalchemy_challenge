from flask import Flask, jsonify
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

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
def home():
    return (
        f"#################################################################################<br/>"
        f"Welcome to Climate API of Honolulu, Hawaii!<br/>"
        f"#################################################################################<br/>"
        f"Here are the list of available routes:<br/>"
        f"#################################################################################<br/>"
        f"/api/v1.0/precipitation ------------- Returns a JSON list of precipitation.<br/>"
        f"<br/>"
        f"/api/v1.0/stations ------------------ Returns a JSON list of weather stations from the dataset.<br/>"
        f"<br/>"
        f"/api/v1.0/tobs ---------------------- Returns a JSON list of temperature observations (TOBS) of the most active station for the previous year.<br/>"
        f"<br/>"
        f"/api/v1.0/2015-01-12 ---------------- Calculates TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.<br/>" 
        f"<br/>"
        f"/api/v1.0/2016-01-12/2016-01-22 ---- Calculates TMIN, TAVG, and TMAX for dates between the start and end date.<br/>"
        )
        
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(bind = engine)

    prcp_result = session.query(Measurement.date, func.sum(Measurement.prcp), Measurement.station).\
        group_by(Measurement.date).order_by(Measurement.date).all()
    
    session.close()

    prcp_list=[]
    
    for row in prcp_result:
        result = list(np.ravel(row)) # Convert list of tuples into normal list
        precipitation_dict = {result[0]:result[1], "Station":result[2]}
        prcp_list.append(precipitation_dict)
    return jsonify(prcp_list)

#################################################

@app.route("/api/v1.0/stations")
def stations():

    session = Session(bind = engine)
    stn = session.query(Station.station, Station.name).all()
    
    session.close()

    stn_list = []

    for row in stn:
        stn_result = list(np.ravel(row))
        stn_dict = {"Station": stn_result[0], "Name":stn_result[1]}
        stn_list.append(stn_dict)
    return jsonify(stn_list)

#################################################

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(bind = engine)

    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date = dt.datetime.strptime(latest[0], '%Y-%m-%d') # Converting format from String to Date 
    year_ago = latest_date - dt.timedelta(days=365)

    active_stn = session.query(Measurement.station, func.count(Measurement.tobs)).\
        group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).first()[0]
    
    tobs_result = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station==active_stn).filter(Measurement.date>=year_ago).all()
    
    session.close()
    
    tobs_list=[]
    
    for row in tobs_result:
        result = list(np.ravel(row)) # Convert list of tuples into normal list
        tobs_dict = {result[1]:result[2], "Station":result[0]}
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

#################################################    

@app.route("/api/v1.0/<start>")
def calc_temp(start):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    session = Session(bind = engine)
    
    temp_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.close()

    temp_list = []

    for row in temp_result:
        temp_data = list(np.ravel(row))
    
        temp_dict = {"Date":temp_data[0], "Min Temp":temp_data[1], "Avg Temp":temp_data[2],\
            "Max Temp":temp_data[3]}

        temp_list.append(temp_dict)

    return jsonify(temp_list)

#################################################

@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    session = Session(bind = engine)

    temp_result = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).\
            group_by(Measurement.date).all()

    session.close()

    temp_list = []

    for row in temp_result:
        temp_data = list(np.ravel(row))
    
        temp_dict = {"Date":temp_data[0], "Min Temp":temp_data[1], "Avg Temp":temp_data[2],\
            "Max Temp":temp_data[3]}

        temp_list.append(temp_dict)

    return jsonify(temp_list)



if __name__ == "__main__":
    app.run(debug=True)
