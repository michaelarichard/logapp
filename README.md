# Sensor LOGAPP

## Vision:
Post a log file or url path to parse and return expected reponse.  
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

Post log file, ignoring self-signed cert when testing localhost.
```
# logfile (local log post)
curl -k -F 'file=@data/example.log' https://localhost/logfile

# logpath (url to remote log)
curl -k -X POST -d 'logpath=https://raw.githubusercontent.com/michaelarichard/logapp/main/data/example.log' https://localhost/logpath
```


### or if k8s context is available. 
  edit skaffold.yaml, it is currently hardcoded to my domain/ingress. Left it up, feel free to test!
```
# continuous deploy on edit, somtimes buggy and requires ctrl-d + rerun
skaffold dev

or 

# single build + deploy
skaffold run

```
```
curl -X POST -F file=@data/example.log https://logapp.stormpath.net/logfile  | jq
curl -X POST -d 'logpath=https://raw.githubusercontent.com/michaelarichard/logapp/main/data/example.log' https://logapp.stormpath.net/logpath
```

## endpoints
### /logfile
 - POST a file to scan as the 'file' param
### /logpath
 - POST a url to scan as the 'logpath' param

## Time tracking
 - 45 mins, Setup project, copy existing hello world docker-compose flaskapi app framework, setup test file, name objects, prepare/cleanup local docker test env.
 - 1hr add helm chart w/ skaffold and determine curl post file - parse / response
 - 3 distracted/interrupted hrs writing code to parse log file and calculate pass/fail - Not done yet but close. (see output below)
 - Hit time limit working on working out numpy/statistics math tests and formatting of result response.
 - After communicating status, added another hour+ to finalize result response, and threw in the logpath option for fun. 

## Recommendations
- Log file format -> into complete json objects,  including type, id, and ref data in all lines. 
- copntinue refactoring a lot into functions for easier maintainable and support of more sensor types. a handler? might scale better.
- Add tests/validation along with verbosity/debug output flags.


## Status

### Next steps
- DONE - Complete result reponse building.
- DONE - Would be nice to add an endpoint to pass a log url pointing to something like s3 bucket instead of posting the whole file. would scale better.
- TODO - Add validation/safe inputs, etc. More tests, etc. 

### Examples

#### Post the whole log file. 
```
curl -X POST -k -F file=@data/example.log https://logapp.stormpath.net/logfile  | jq                                                      
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   947  100    85  100   862    607   6162 --:--:-- --:--:-- --:--:--  7367
{
  "temp-1": "precise",
  "temp-2": "ultra precise",
  "hum-1": "keep",
  "hum-2": "discard"
}
```
##### Post a log file by url (More scalable, allows hosting of files somewhere like s3)
```
curl -X POST -d 'logpath=https://raw.githubusercontent.com/michaelarichard/logapp/main/data/example.log' https://logapp.stormpath.net/logpath | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   171  100    85  100    86    387    391 --:--:-- --:--:-- --:--:--   432
{
  "temp-1": "precise",
  "temp-2": "ultra precise",
  "hum-1": "keep",
  "hum-2": "discard"
}
```
### hidden output (TODO: make this visible w/ a debug flag)
```
➜  logapp git:(master) ✗ curl -X POST -k -F file=@data/example.log https://logapp.stormpath.net/logfile  | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1376  100   514  100   862   3777   6335 --:--:-- --:--:-- --:--:--  7495
{
  "results": {
    "temp-1": "precise",
    "temp-2": "ultra precise",
    "hum-1": "keep",
    "hum-2": "discard"
  },
  "input_data": {
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
        "stddev": 5.397898451463096,
        "ref_humid": 45,
        "ref_temp": 70
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
        "stddev": 0.9044335243676014,
        "ref_humid": 45,
        "ref_temp": 70
      }
    },
    "humidity": {
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
}
```