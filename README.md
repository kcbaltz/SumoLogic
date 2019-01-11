# SumoLogic Source Management API

This is a utility to manage sources on multiple Sumo Logic Collectors at once.  It currently allows you to add and update sources using the SumoLogic REST API

It uses substrings or regular expressions to work with a subset of all the collectors on your account.  With it, you can mass-update similar collectors and sources.  

# Examples
## Find all the collectors who have "web" in their name

````
> sumoUtil.py -c web 
Test mode enabled.  Disable with -T
# svrweb001.example.com
# svrweb002.example.com
# svrweb003.example.com
# svrweb004.example.com
````

## Find the 002 and 003 "web" collectors by regex:

````
> sumoUtil.py -r ".*web00[23].*" 
Test mode enabled.  Disable with -T
# svrweb002.example.com
# svrweb003.example.com
````

## Show the Sources for those collectors
````
> sumoUtil.py -r ".*web.*" -s 
Test mode enabled.  Disable with -T
# svrweb001.example.com
{
    "sources": [
        {
             ...
        }
    ]
}
# svrweb002.example.com
{
    "sources": [
        {
             ...
        }
    ]
}
````

## Add a source to a set of collectors 
(append -T to disable test mode which doesn't actually change anything)
````
> sumoUtil.py -r ".*web.*" -i source.json -o ADD 
svrweb001.example.com
POST'ing the following to https://api.sumologic.com/api/v1/collectors/11233482736/sources
{
    "source": {
            ...
    }
}
<Response [201]>
201
svrweb002.example.com
POST'ing the following to https://api.sumologic.com/api/v1/collectors/11233482736/sources
{
    "source": {
            ...
    }
}
<Response [201]>
201
````
## Update a source by name
(append -T to disable test mode which doesn't actually change anything)
````
> sumoUtil.py -r ".*web.*" -i source.json -o UPDATE 
svrweb001.example.com
Would PUT the following to https://api.sumologic.com/api/v1/collectors/13453457/sources/12345678
{
    "source": {
        ...
    }
}
````



# Notes
+ When using ADD/UPDATE, the script will modify the cutoffTimestamp (or add one) set to 24 hours prior.  This is to avoid a large spike in ingestion rates.  Let me know if you want a flag added to make this optional.

# Requirements
+ Python 3.x
+ Requests  [http://docs.python-requests.org/en/latest/]

# Setup
+ Copy config.ini-TEMPLATE to config.ini and then fill it in with the access key from your account.
+ Grant execute permission to the script:  chmod u+x sumoUtil.py


# Usage
````
./sumoUtil.py --help
usage: sumoUtil.py [-h] [-c COLLECTORPATTERN] [-r COLLECTORREGEX] [-C] [-s]
                   [-o OPERATION] [-i INFILE] [-T]

Get Collectors

optional arguments:
  -h, --help            show this help message and exit
  -c COLLECTORPATTERN, --collectorPattern COLLECTORPATTERN
                        Collector name substring to search for
  -r COLLECTORREGEX, --collectorRegex COLLECTORREGEX
                        Collector name regex to search for
  -C, --printCollectors
                        Default: true
  -s, --printSources    Dump Sources
  -o OPERATION, --operation OPERATION
                        Operation (ADD|UPDATE)
  -i INFILE, --infile INFILE
                        Input File (JSON)
  -T, --disableTestMode
                        Disable Test Mode
````

# Sample JSON
The JSON for the collector should be according to SumoLogic's Collector Management API [https://github.com/SumoLogic/sumo-api-doc/wiki/Collector-Management-API].  

````
{
    "source": 
        {
            "name": "web_access",
            "alive": true,
            "automaticDateParsing": true,
            "blacklist": [],
            "category": "Application_Web_Apache",
            "encoding": "UTF-8",
            "filters": [],
            "forceTimeZone": false,
            "multilineProcessingEnabled": false,
            "pathExpression": "/var/apache2/log/access.log",
            "sourceType": "LocalFile",
            "timeZone": "America/Los_Angeles",
            "useAutolineMatching": true
        }
}
````

For now, I recommend using the -s switch to view the JSON source of a collector you configure through the web and then modify that source for ADD'ing to other collectors.  You'll also need to replace the "sources" array with just a single "source" element.  The API does not appear to allow you to add more than one source at a time to a given collector.  Be sure to remove the following:

+ id 
+ cutoffTimestamp   -- The script will automatically modify this to 24 hours ago if you leave it in.  
 
When UPDATE'ing, be sure the name matches as that is what is used to identify the source to be replaced.  

(In the future, I'd like this utility to help with generating the source by taking the output of -s, stripping the unwanted fields and converting the "sources" field to "source", possibly with an automatic COPY option to clone the source from one collector to another. )
