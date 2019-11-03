from flask import Flask , jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt 
from sqlalchemy.orm import scoped_session, sessionmaker
#############################################
# Database Setup
#############################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo=False)

Base = automap_base()

Base.prepare(engine, reflect=True)



Measurement = Base.classes.measurement
Station = Base.classes.station


session = scoped_session(sessionmaker(bind=engine))

last_date = session.query(
	Measurement.date
).order_by(
	Measurement.date.desc()
).first()[0]
last_date = dt.datetime.strptime(last_date,"%Y-%m-%d")
first_date = last_date - dt.timedelta(days = 365)


############################################
# Flask Setup
############################################

app = Flask(__name__)

############################################
# Flask Setup
############################################

@app.route("/")
def welcome():

    return (
        f"Available Routes:<br/>"
        f"The dates and temperature observations from the last year:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"List of stations from the dataset:<br/>"
        f"/api/v1.0/stations<br/>"
        f"List of Temperature Observations (tobs) for the previous year:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"List of the minimum temperature, the average temperature, and the max temperature for a given start(i.e.2017-1-1):<br/>"
        f"/api/v1.0/<start><br/>"
        f"List of the minimum temperature, the average temperature, and the max temperature for a given start and end(i.e.2017-01-01/2017-01-07):<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
	
	twelve_month_data = session.query(
    Measurement.date,
    Measurement.prcp
	).filter(
    Measurement.date > first_date
	).order_by(
    Measurement.date
	).all()

	precipitation_data = dict(twelve_month_data)

	return jsonify({'Data':precipitation_data})

@app.route("/api/v1.0/stations")
def stations():
	stations = session.query(Station).all()
	stations_list = list()
	for station in stations:
		stations_dict = dict()
		stations_dict['Station'] = station.station
		stations_dict["Station Name"] = station.name
		stations_dict["Latitude"] = station.latitude
		stations_dict["Longitude"] = station.longitude
		stations_dict["Elevation"] = station.elevation
		stations_list.append(stations_dict)

	return jsonify ({'Data':stations_list})

@app.route("/api/v1.0/tobs")
def tobs():

	twelve_month_tobs = session.query(
    	Measurement.tobs,
    	Measurement.date,
    	Measurement.station    

	).filter(
    	Measurement.date > first_date
	).all()

	temp_list = list()
	for data in twelve_month_tobs:
		temp_dict = dict()
		temp_dict['Station'] = data.station
		temp_dict['Date'] = data.date
		temp_dict['Temp'] = data.tobs
		temp_list.append(temp_dict)

	return jsonify ({'Data':temp_list})

@app.route("/api/v1.0/<start>")
def start_temp(start=None):

	start_temps = session.query(
		func.min(Measurement.tobs), 
		func.avg(Measurement.tobs),
		func.max(Measurement.tobs)
	).filter(
		Measurement.date >= start
	).all()


	start_list = list()
	for tmin, tavg, tmax in start_temps:
		start_dict = {}
		start_dict["Min Temp"] = tmin
		start_dict["Max Temp"] = tavg
		start_dict["Avg Temp"] = tmax
		start_list.append(start_dict)

	return jsonify ({'Data':start_list})



@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start=None,end=None):
    temps = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(
    	Measurement.date >= start,
    	Measurement.date <= end
    ).all()

    temp_list = list()
    for tmin, tavg, tmax in temps:
    	temp_dict = dict()
    	temp_dict["Min Temp"] = tmin
    	temp_dict["Avg Temo"] = tavg
    	temp_dict["Max Temp"] = tmax
    	temp_list.append(temp_dict)

    return jsonify ({'Data':temp_list})
 



if __name__ == '__main__':
    app.run(debug=True)