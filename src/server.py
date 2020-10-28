from flask import Flask, request, make_response, url_for
from flask_api import FlaskAPI, status, exceptions
import json
from io import StringIO
from werkzeug.utils import secure_filename
import re
import statistics
app = FlaskAPI(__name__)


@app.route('/')
def index():
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
#     """
#     Accept a file and parse to return the output.
#     """
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

    # TODO: Refactor into testable, maintanable functions.
    # TODO: Propose new log format
    ref_string = ("reference")
    sensor_types = ("thermometer", "humidity")
    timestamp_regex = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}'
    sensors = {}

    # parse this ugly log file into dictionaries to process
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
            sensors[s_type][s_name]['values'].append(float(value))
            float_values = list(map(float, sensors[s_type][s_name]['values']))
            sensors[s_type][s_name]['mean'] = statistics.mean(float_values)

            if len(float_values) >= 2:
                sensors[s_type][s_name]['stddev'] = statistics.stdev(float_values)

    # Calculate pass/fail status
    # and then return result
    sensors['humidity']['reference'] = ref_humid
    sensors['thermometer']['reference'] = ref_temp
    result = process_data(sensors)
    # result = sensors
    return result

def process_data(data):
    result = {}
    for sensor_type in data:
        if sensor_type is 'thermometer':
            # refactor to function
            # temp_result = process_temp(data[sensor_type])
            #  Calculate rating
            # "ultra precise" if the mean of the readings is within 0.5 degrees of the known temperature, and the standard deviation is less than 3.
            # "very precise" if the mean is within 0.5 degrees of the room, and the standard deviation is under 5
            # "precise"
            for s in data[sensor_type]:
                result[s] = 'skip'

        if type is 'humidity':
            #  Calculate result
            # humid_result = process_humid(data[sensor_type])
            #
            for s in data[sensor_type]:
                result[s] = 'skip'
    return data