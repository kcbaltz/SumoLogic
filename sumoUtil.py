#!/usr/bin/env python3
#
# Author: KC Baltz
#
import sys, json, os, argparse, re
# http://docs.python-requests.org/en/latest/
import requests 
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

username = config.get('Sumo', 'username', fallback=None)
password = config.get('Sumo', 'password', fallback=None)

if username is None or password is None:
    print("Can't find username or password in config.ini")
    sys.exit(1)

parser = argparse.ArgumentParser(description='Get Collectors')
parser.add_argument('-c', '--collectorPattern', dest='collectorPattern', action='store', required=False, help='substring to search for')
parser.add_argument('-x', '--excludeCollectorPattern', dest='excludeCollectorPattern', action='store', required=False, help='Exclude collectors matching this substring')
parser.add_argument('-C', '--printCollectors', dest='printCollectors', action='store_const', const=True, required=False, help='print(JSON')
parser.add_argument('-s', '--printSources', dest='printSources', action='store_const', const=True, required=False, help='Dump Sources')
parser.add_argument('-o', '--operation', dest='operation', action='store', required=False, help='Operation (ADD|...)')
parser.add_argument('-i', '--infile', dest='infile', action='store', default=None, required=False, help='Input File (JSON)')
parser.add_argument('-T', '--disableTestMode', dest='testMode', action='store_const', const=False, default=True, required=False, help='Disable Test Mode')
args = parser.parse_args()

if args.testMode: 
    print("Test mode enabled.  Disable with -T")

r = requests.get("https://api.sumologic.com/api/v1/collectors?limit=10000", auth=(username, password))       

collectorData = r.json()
# Find the right collectors
j = 0
while j<len(collectorData["collectors"]):
    if args.collectorPattern is not None: 
        p = re.compile(args.collectorPattern)

    if args.collectorPattern is None or p.match(collectorData["collectors"][j]["name"]):
        print("# " + collectorData["collectors"][j]["name"])
        sourcesUrl = "https://api.sumologic.com/api/v1/collectors/" + str(collectorData["collectors"][j]["id"]) + "/sources"
        if args.printCollectors:
            print(json.dumps(collectorData["collectors"][j]))
        if args.printSources:
            r = requests.get("https://api.sumologic.com/api/v1/collectors/" + str(collectorData["collectors"][j]["id"]) + "/sources", auth=(username, password))
            sourceJson = r.json()
            print(json.dumps(sourceJson, indent=4, sort_keys=True ))
        if args.operation == "ADD":    
            # curl -X POST -H "Content-Type: application/json" -T abelog.json https://api.sumologic.com/api/v1/collectors/102987943/sources
            if args.infile is None:
                print("infile not defined.")
                sys.exit(1)
            try:
                inputJsonFile = open(args.infile, 'r')
                data = json.load(inputJsonFile)
                inputJsonFile.close()
            except IOError as ex:
                print("Unable to open file (" + args.infile + "):  " + str(ex) + "\n")
                sys.exit(1)


            if args.testMode:
                print("Would POST the following to " + sourcesUrl)
                print(json.dumps(data, indent=4, sort_keys=True ))
            else:
                # Do it 
                print("POST'ing the following to " + sourcesUrl)
                print(json.dumps(data, indent=4, sort_keys=True ))
                headers = {'Content-Type': 'application/json'}
                
                r = requests.post(sourcesUrl, json=data, auth=(username, password), headers=headers)
                r.json()
                print (r)
                print (r.status_code)

        if args.operation == "UPDATE":    
            if args.infile is None:
                print("infile not defined.")
                sys.exit(1)
            try:
                inputJsonFile = open(args.infile, 'r')
                data = json.load(inputJsonFile)
                inputJsonFile.close()
            except IOError as ex:
                print("Unable to open file (" + args.infile + "):  " + str(ex) + "\n")
                sys.exit(1)


            # Find ETAG for source to update
            r = requests.get("https://api.sumologic.com/api/v1/collectors/" + str(collectorData["collectors"][j]["id"]) + "/sources", auth=(username, password))
            r.headers
            sourceJson = r.json()

            k = 0
            sourceUrl = None
            found = False
            for source in sourceJson["sources"]:
                print(source["name"])
                if sourceJson["sources"][k]["name"] == data["source"]["name"]:
                    sourceUrl = "https://api.sumologic.com/api/v1/collectors/" + str(collectorData["collectors"][j]["id"]) + "/sources/" + str(source["id"])
                    r2 = requests.get(sourceUrl, auth=(username, password))
                    etag = r2.headers["etag"]
                    print("Found matching source: " + source["name"] + " with ETAG " + etag)
#                    print(json.dumps(source, indent=4, sort_keys=True ))
                    found = True

            if found is False:
                print("No source found to match: " + data.name)
                sys.exit(1)
    
            # replace the id so we get a good match
            data["source"]["id"] = source["id"] 
            if args.testMode:
                ## Add Header for If-Match
                print("Would PUT the following to " + sourceUrl)
                print(json.dumps(data, indent=4, sort_keys=True ))
            else:
                # Do it 
                print("PUT'ing the following to " + sourceUrl)
                print(json.dumps(data, indent=4, sort_keys=True ))
                headers = {'Content-Type': 'application/json', 'If-Match': etag }
                
                r = requests.put(sourceUrl, json=data, auth=(username, password), headers=headers)
                r.json()
                print (r)
                print (r.status_code)

    j = j + 1
