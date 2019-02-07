# LogSearch API

[![Build Status](https://api.travis-ci.org/seamusc/lepy.svg?branch=master)](https://travis-ci.org/seamusc/lepy)

lepy is a Python library to enable access to the Rapid7 [Log Search API](https://insightops.help.rapid7.com/docs/using-log-search) in an easy to use, programatic manner. 


### Install

```
python setup.py install
```

### Example usage

```
>>> from logsearch.logsearch import LogSearch
>>> ls = LogSearch(api_key=API_KEY)
>>> my_log_key = 'e1dc8460-c28e-434e-b990-dd0faea894a8'
>>> query = 'where(response_code=500) calculate(count)'
>>> result = ls.search(log_keys=[my_log_key], query=query, time_range='Last 24 Hours')
Progress |################################| 100% 4s 0:00:00
>>> print result.display()
{
    "during": {
        "from": 1548706511751, 
        "time_range": "last 24 hours", 
        "to": 1548792911751
    }, 
    "statement": "where(response_code=500) calculate(count)"
}
Statistics response calculate( count )
Timestamp                   count
------------------------  -------
28/01/19 20:15:11.751000       92
28/01/19 17:51:11.751000       33
28/01/19 15:27:11.751000       12
28/01/19 13:03:11.751000       13
28/01/19 10:39:11.751000       14
28/01/19 08:15:11.751000      134
28/01/19 05:51:11.751000       80
28/01/19 03:27:11.751000      105
28/01/19 01:03:11.751000      386
27/01/19 22:39:11.751000      101
```


### Notes
Visual progress bar will not be shown if following dependencies are not installed:
 - `tabulate`
 - `progress`

To enable visual progress bar run following instruction:

 ```pip install tabulate progress```
