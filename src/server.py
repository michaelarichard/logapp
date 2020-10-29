from flask import Flask, request, make_response, url_for
from flask_api import FlaskAPI, status, exceptions
import json
from io import StringIO
from werkzeug.utils import secure_filename
import re
import statistics
from decimal import Decimal
app = FlaskAPI(__name__)


@app.route('/')
def index():
    """
    Default route, used as a health/readiness check for k8s deployment and troubleshooting of source IP
    Could be expanded to included more intelligence for a complex healthcheck
    """
    content = "Hello World."
    fwd_for = "X-Forwarded-For: {}".format(
        request.headers.get('x-forwarded-for', None)
    )
    real_ip = "X-Real-IP: {}".format(
        request.headers.get('x-real-ip', None)
    )
    fwd_proto = "X-Forwarded-Proto: {}".format(
        request.headers.get('x-forwarded-proto', None)
    )

    output = "\n".join([content, fwd_for, real_ip, fwd_proto])
    response = make_response(output, 200)
    response.headers["Content-Type"] = "text/plain"

    return response

@app.route('/logfile', methods=['POST','PUT'])
def task_postlog():
    """
    Accept a file and parse to return the output.
    """
    if request.method == 'GET':
        return "post a file"
    else:
        logfile = request.files['file']
        if logfile:
            result = parselogs(StringIO(logfile.read().decode()))
            resp = make_response(result)
            resp.status_code = 200
            return resp
            # filename = secure_filename(logfile.filename)
            # return filename

def parselogs(logfile):
    """
    Parse existing logfile format.
    Propose new log format
    A json format log file w key, value including name, type, ref, time, and value for each sample line would allow us to simplify this parsing loop
    """
    ref_string = ("reference")
    sensor_types = ("thermometer", "humidity")
    timestamp_regex = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}'
    sensors = {}

    # parse the log file into dictionaries to process
    for line in logfile:
        # find reference line
        if ref_string in line:
            ref_temp = line.split()[1]
            ref_humid = line.split()[2]

        # find sensor lines which signals start of new sensor
        if any(t in line for t in sensor_types):
            s_type = line.split()[0]
            s_name = line.split()[1]
            # add type if not exists yet
            if s_type not in sensors:
                sensors[s_type] = {}
            if s_name not in sensors[s_type]:
                # New sensor, setup defaults
                sensors[s_type][s_name] = {}
                sensors[s_type][s_name]['values'] = []
                sensors[s_type][s_name]['mean'] = 0
                sensors[s_type][s_name]['stddev'] = 0
        # find data lines to append to dataset
        if re.match(timestamp_regex, line):
            timestamp = line.split()[0]
            value = line.split()[1]
            sensors[s_type][s_name]['values'].append(Decimal(value))
            float_values = list(map(Decimal, sensors[s_type][s_name]['values']))
            sensors[s_type][s_name]['mean'] = statistics.mean(float_values)
            sensors[s_type][s_name]['ref_humid'] = Decimal(ref_humid)
            sensors[s_type][s_name]['ref_temp'] = Decimal(ref_temp)
            if len(float_values) >= 2:
                sensors[s_type][s_name]['stddev'] = statistics.stdev(float_values)

    # Calculate rating
    # and then return result
    result = process_data(sensors)
    return result['results']
    # Suggest returning full result with input values might assist with troubleshooting bad input data later.
    # return result

def process_data(data):
    result = {}
    result['results'] = {}
    for sensor_type in data:
        output = sensor_type
        if sensor_type in 'thermometer':
            for s in data[sensor_type]:
                result['results'][s] = validate_temp(data[sensor_type][s])
    
        if sensor_type in 'humidity':
            for s in data[sensor_type]:
                result['results'][s] = validate_humid(data[sensor_type][s])
    result['input_data'] = data
    return result


def validate_humid(data):
    """
    For a humidity sensor, it must be discarded unless it is within 1 humidity percent of the reference value for all readings. (All humidity sensor
    readings are a decimal value representing percent moisture saturation.)
    """
    ref_humid = data['ref_humid']
    values = data['values']
    rating = 'keep' # default
    for v in values:
        if abs(Decimal(ref_humid) - Decimal(v)) > 1 :
            rating = 'discard'
    return rating

def validate_temp(data):
    """
    Calculate rating of a temp sensor
    "ultra precise" if the mean of the readings is within 0.5 degrees of the known temperature, and the standard deviation is less than 3.
    "very precise" if the mean is within 0.5 degrees of the room, and the standard deviation is under 5
    "precise"
    """
    ref_temp = data['ref_temp']
    mean = data['mean']
    stddev = data['stddev']
    if abs(Decimal(ref_temp) - Decimal(mean)) < Decimal(0.5) and stddev < 3 :
        rating = 'ultra precise'
    elif abs(Decimal(ref_temp) - Decimal(mean)) < Decimal(0.5) and stddev < 5 :
        rating = 'very precise'
    else:
        rating = 'precise'
    return rating