# Sensor LOGAPP

## Vision:
curl Post log files, parse and return expected reponse.  
- microservice API/scalable
- deployable to k8s
- no local disk/streaming concerns.

## Setup

Starting with a simple python flaskAPI app, running in a container. 
(Copied from previous personal example hello-world microservice app best practices, secure SSL, gunicorn + local dev src mounted)

local dev started w/ nginx reverse proxy for local testing/development to simulate a simple k8s ingress.
- allows for testing of forwarded headers, multiple services, ssl, etc as if in k8s. 

Adding a helm chart + skaffold.yaml to skaffold dev on k8s.  ( Prerequisite: Requires docker.io or other container repo setup to transfer/deploy )

Parse log file and return expected response. 

## Usage

### local docker
```
docker-compose up

```

Post log file, ignoring self-signed cert for now.
```
curl -k -F 'file=@data/example.log' https://localhost/logfile
```


### or if k8s context is available. (edit skaffold.yaml is currently hardcoded to my domain/ingress)
```
skaffold dev
```
```
curl -X POST -k -F file=@data/example.log https://logapp.stormpath.net/logfile  | jq
```

## Time tracking
 - 45 mins, Setup project, copy existing hello world docker-compose flaskapi app framework, setup test file, name objects, prepare/cleanup local docker test env.
 - 1hr add helm chart w/ skaffold and determine curl post file - parse / response
 - 3 distracted/interrupted hrs writing code to parse log file and calculate pass/fail - Not done yet but close. (see output below)
 - Hit time limit working on working out numpy/statistics math tests and formatting of result response.

## Recommendations
- Log file format -> into complete json objects,  including type, id, and ref data in all lines. 
- copntinue refactoring a lot into functions for easier maintainable and support of more sensor types. 
- Add tests


## Status

### Next steps

Need to add an if range()? and if within ref value and build the response object.
https://github.com/michaelarichard/logapp/blob/main/src/server.py#L95-L117

Would be nice to add an endpoint to pass a log url pointing to something like s3 bucket instead of posting the whole file. would scale better.

### current output
```
➜  logapp git:(master) ✗ curl -X POST -k -F file=@data/example.log https://logapp.stormpath.net/logfile  | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1376  100   514  100   862   3777   6335 --:--:-- --:--:-- --:--:--  7495
{
  "results": {
    "temp-1": "skip",
    "temp-2": "skip",
    "hum-1": "skip",
    "hum-2": "skip"
  },
  "input_data": {
    "hum-1": {
      "values": [
        45.2,
        45.3,
        45.1
      ],
      "mean": 45.2,
      "stddev": 0.09999999999999787,
      "ref_humid": 45,
      "ref_temp": 70
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
      "stddev": 1.0568822072492268,
      "ref_humid": 45,
      "ref_temp": 70
    }
  }
}
```