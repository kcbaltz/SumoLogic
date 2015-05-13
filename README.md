# SumoLogic Source Management API

This is a utility to manage sources on multiple Sumo Logic Collectors at once.  It currently allows you to add and update sources using the SumoLogic REST API

It uses regular expressions to work with a subset of all the collectors on your account.

# Requirements
+ Python 3.x
+ Requests  [http://docs.python-requests.org/en/latest/]

# Setup
Copy config.ini-TEMPLATE to config.ini and then fill it in with the access key from your account. 

#Examples

````
# find all the collectors who have "web" in their name
> sumoUtil.py -c ".*web.*" 
Test mode enabled.  Disable with -T
# svrweb001.example.com
# svrweb002.example.com

# Show the Sources for those collectors
> sumoUtil.py -c ".*web.*" -s 
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
````
