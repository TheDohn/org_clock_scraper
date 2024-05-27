# this is just in case I need to pull data from historical tickets to see
# what keys correspond to what billable types in Jira
import requests
import os
from datetime import date
import re
import json

import pandas as pd

from requests.auth import HTTPBasicAuth

# this DOES work
# 3.0 API way
base_tempo_url = "https://api.tempo.io/core/3"
# base_tempo_url = "https://api.tempo.io/4"
test_req = requests.get(
                # url = base_tempo_url + "/worklogs/user/" + os.getenv('TEMPO_AUTHOR_ACCOUNT_ID') + "?from=2021-06-21&to=2021-06-24",
                url = base_tempo_url + "/worklogs/user/" + os.getenv('TEMPO_AUTHOR_ACCOUNT_ID') + "?from=2024-05-20&to=2024-05-20",
                headers = { "Authorization": "Bearer " + os.getenv('TEMPO_BEARER_TOKEN') }
                       )

# trying 4.0 API way
# base_tempo_url = "https://api.tempo.io/4"
# test_req = requests.get(
#                 url = base_tempo_url + "/worklogs",
#                 # headers = { "Authorization": "Bearer " + os.getenv('TEMPO_BEARER_TOKEN') },
#                 headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + os.getenv('TEMPO_BEARER_TOKEN')},
#                 # data     =  json.dumps({'foo'})
#                 data     =  json.dumps({
#                     'from':'2024-05-10',
#                     'to':'2024-05-10',
#                     'limit': 10
#                     })
#                        )


print(dir(test_req))

# print(test_req.status_code)


# print(test_req.json()['results'])

# X = 0
# print(test_req.json()['results'][X]['attributes']['values'][0]['value'])

# X = -1
# print(test_req.json()['results'][X]['attributes']['values'])#['value'])
# print(test_req.json()['results'])#['value'])

# for r in test_req.json()['results']:
#     print(r)
#     print("\n")


# print(test_req.json()['results'])#['value'])
# print(test_req.json())#['value'])

# #easiest to look at this in a json editor to see where these are nested
# billable_values = []
# for r in test_req.json()['results']:
#     billable_values.append(r['attributes']['values'][1]['value'])

# unique_billable_values = list(set(billable_values))
# print(unique_billable_values)


# # something seems to have changed, since the [1] above used to work, I think,
# # and now I needed to replace that with [0] below
# billable_values = []
# for r in test_req.json()['results']:
#     billable_values.append(r['attributes']['values'][0]['value'])

# unique_billable_values = list(set(billable_values))
# print(unique_billable_values)
