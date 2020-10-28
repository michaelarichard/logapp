# CMG_APP

## Vision:
curl Post log files, parse and return expected reponse.  
- microservice API/scalable
- deployable to k8s
- no local disk/streaming concerns.

## Setup
Starting with a simple python flaskAPI app, running in a container. 
(Copied from previous personal work, example hello-world microservice app best practices, secure SSL, gunicorn + local dev src mounted)

Using nginx reverse proxy for local testing/development to simulate a simple k8s ingress.
- allows for testing of forwarded headers, multiple services, ssl, etc as if in k8s. 


TODO: Adding a helm chart + skaffold.yaml to skaffold dev on k8s.  ( Prerequisite: Requires docker.io or other container repo setup to transfer/deploy )

TODO: Parse log file and return expected response. 

## Usage

```
docker-compose up
```

Post log file, ignoring self-signed cert for now.
```
curl -k -F 'log_file=@data/example.log' https://localhost/upload
```

# Time log: 
 - 45 mins, Setup project, copy existing hello world flaskapi app framework, setup test file, name objects, prepare/cleanup local docker test env.
 - 1hr add helm chart w/ skaffold
 - postfile flask - parse / response
 - + 3 distracted hrs writing code to parse log file and calculate pass/fail - Not done yet but close. 
 - Hit time limit working on working out math tests and formatting of result response.

Recommendations: 
- Log file format -> into complete json objects, possibly including type, id, and ref data in all lines. 
- Add tests
- refactor a lot into functions for easier maintainable and support of more sensor types. 



```
➜  cmg_app git:(master) ✗ curl -X POST -k -F file=@data/example.log https://logapp.stormpath.net/logfile  | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1376  100   514  100   862   3777   6335 --:--:-- --:--:-- --:--:--  7495
{
  "thermometer": {
    "temp-1": {
      "values": [
        72.4,
        76,
        79.1,
        75.6,
        71.2,
        71.4,
        69.2,
        65.2,
        62.8,
        61.4,
        64,
        67.5,
        69.4
      ],
      "mean": 69.63076923076923,
      "stddev": 5.397898451463096
    },
    "temp-2": {
      "values": [
        69.5,
        70.1,
        71.3,
        71.5,
        69.8
      ],
      "mean": 70.44,
      "stddev": 0.9044335243676014
    },
    "reference": "70.0"
  },
  "humidity": {
    "hum-1": {
      "values": [
        45.2,
        45.3,
        45.1
      ],
      "mean": 45.2,
      "stddev": 0.09999999999999787
    },
    "hum-2": {
      "values": [
        44.4,
        43.9,
        44.9,
        43.8,
        42.1
      ],
      "mean": 43.82,
      "stddev": 1.0568822072492268
    },
    "reference": "45.0"
  }
}
➜  cmg_app git:(master) ✗ 
```