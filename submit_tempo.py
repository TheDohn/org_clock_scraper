import requests
import os
from datetime import date
import re
import json
from termcolor import cprint

# TODO:

# this is a bit overkill, but it works
# I want to capture the org table that starts like this:
#  #+BEGIN: clocktable :scope subtree :maxlevel 4
#  #+CAPTION: Clock summary at [2021-06-10 Thu 18:55]
#  | Headline                                         | Time   |   |      |      |
#  |--------------------------------------------------+--------+---+------+------|
#  | *Total time*                                     | *9:42* |   |      |      |
#  |--------------------------------------------------+--------+---+------+------|
#  | \_    <2021-06-10 Thu>
prior_lines = ['NA']*7
today = date.today().strftime('%Y-%m-%d') # for actually running the script daily
# today = '2023-10-27' # in case I need to run this for a specific day
#today = '2021-06-04' # just for testing
#today = '2021-06-19' # for testing with short times
# today = '2024-07-08'
print("Today is", today, "\n")
record = False
record_counter = 0
org_table = []
with open(file = 'IXIS_JOURNAL.org') as f:
    for line in f.readlines():
        # start recording when you find today's org table
        if ('#+BEGIN: clocktable'         in prior_lines[0] and
            '#+CAPTION: Clock summary at' in prior_lines[1] and
            '| Headline'                  in prior_lines[2] and
            '|---------'                  in prior_lines[3] and
            '| *Total time*'              in prior_lines[4] and
            '|---------'                  in prior_lines[5] and
            today                         in prior_lines[6] ):

            record = True

        if record and '#+END' in line:
            record_counter += 1
            record = False
            if record_counter > 1:
                raise Exception('More than 1 org table found for today:', today )
                break
        if record:
            org_table.append(line)
        # else shift all the current lines
        else:
            prior_lines[0] = prior_lines[1]
            prior_lines[1] = prior_lines[2]
            prior_lines[2] = prior_lines[3]
            prior_lines[3] = prior_lines[4]
            prior_lines[4] = prior_lines[5]
            prior_lines[5] = prior_lines[6]
            prior_lines[6] = line

if prior_lines == ['NA']*7 or org_table == []:
    raise Exception('There was an error reading in the org table (likely no table for todays date found).')


bill_type_dict = {
                'B-B'   : 'B|Billable',
                'NB-P'  : 'NB|Platform',
                'NB-T'  : 'NB|TeamOps',
                'NB-RD' : 'R&D',
                'NB-CM' : 'ProjectManagement',# this is'NB|ClientMeetings',
                'NB-TP' : 'Training&ProDev',
                'NB-PM' : 'NB|ProjectManagement', # actual NB project management
                'NB-BO' : 'AdminOps' #this is BizOps in the Jira/Tempo GUI
                }
org_list = [ ]
# the first 5 entries and the last one are not tickets
# TODO this might be too sensitive to other dashed in the line
# it gives me a "More than 1 ticket found" error if I have [AUDI-1234 B-B] ABCFEF 03-14
# and errors on the second dash, which is outside of the []s??
for org_entry in org_table:
    #remove ticket and billable type in the [] brackets
    desc = re.sub("\[.+\]", '', org_entry)
    #remove time
    desc = re.sub("[0-9]{1,2}:[0-9]{1,2}", '', desc)
    # remove \, _, | from org tables
    desc = re.sub('[\\\_|]', '', desc)
    # remove any to-do counters like [1/5]
    desc = re.sub('\[[0-9]+/[0-9]\]', '', desc)
    # trim whitespace
    desc = re.sub('[ ]+', ' ', desc).strip()
    ticket = re.findall("[A-Z0-9]+-[0-9]+", org_entry)
    if ticket and len(ticket)==1:
        ticket = ticket[0]
    elif ticket and len(ticket)>1:
        print(ticket)
        raise Exception("More than 1 ticket found")
    elif not ticket:
        print(org_entry)
        raise Exception("No ticket found")
    else:
        print(org_entry)
        raise Exception("Ticket error")
    # I care less about billable type, so I wont bother error trapping this
    try:
        bill_type = re.findall("[A-Z]{1,2}-[A-Z]{1,2}", org_entry)[0]
    except Exception as e:
        print('Billable type error for', org_entry)
        raise e
    try:
        bill_type = bill_type_dict[bill_type]
    except Exception as e:
        print(org_entry)
        print(f'For the billable type dict there was an error: {repr(e)}')
        raise e
    #get raw time and then calculate time in seconds
    time_HM = re.findall("[0-9]{1,2}:[0-9]{1,2}", org_entry)
    if time_HM and len(time_HM)==1:
        time_HM = time_HM[0]
    elif time_HM and len(time_HM)>1:
        raise Exception("More than 1 time found.")
    elif not time_HM:
        raise Exception("No time found")
    else:
        raise Exception("Ticket error")
    time_sec = 60*60*int(time_HM.split(':')[0]) + 60*int(time_HM.split(':')[1])
    # work level - this doesn't seem to matter much so just put something reasonable it
    if 'TEAMOPS' in ticket:
        work_level = 'NA'
    else:
        work_level = 'JuniorLevel'
    # construct final dictionary for work log
    # this used to work for the 3.0 API
    curr_dict = {
        'issueKey'        : ticket,
        'timeSpentSeconds': time_sec,
        'startDate'       : today,
        'description'     : desc,
        'authorAccountId' : os.getenv('TEMPO_AUTHOR_ACCOUNT_ID'),
        'attributes'      : [
                # this used to be a thing, but someone dropped it from the interface, which broke my code
                # {
                # 'key'  : '_WorkLevel_',
                # 'value': work_level,
                # },
                {
                 'key'  : '_NonbillableType_',
                 'value': bill_type
                 }
            ]
           #'raw_entry' : org_entry # uncomment to check things
                }
    # trying this for the 4.0 API, which may ultimately need if they deprecate the 3.0 API
    # curr_dict = {
    #     'issueId'         : ticket,
    #     'timeSpentSeconds': time_sec,
    #     'startDate'       : today,
    #     'description'     : desc,
    #     'authorAccountId' : os.getenv('TEMPO_AUTHOR_ACCOUNT_ID'),
    #     'attributes'      : [
    #             {
    #             'key'  : '_WorkLevel_',
    #             'value': work_level,
    #             },
    #             {
    #              'key'  : '_NonbillableType_',
    #              'value': bill_type
    #              }
    #         ]
    #        #'raw_entry' : org_entry # uncomment to check things
    #             }
    #
    org_list.append(curr_dict)

# calculate the total hours
total_time_in_hours = round(sum([e['timeSpentSeconds'] for e in org_list])/(60*60), 2)
print(f'Total time is {total_time_in_hours} hours.')
if total_time_in_hours >= 10:
    print("That was a really long day!\n")

print(f'You have {len(org_list)} tickets\n')
if len(org_list) >=10:
    print("That is a lot of tickets!\n")

# got requests bearer code from:
#https://stackoverflow.com/questions/29931671/making-an-api-call-in-python-with-an-api-that-requires-a-bearer-token
for ticket in org_list:
    request = requests.post(
                url     = 'https://api.tempo.io/core/3/worklogs',
                # url     = 'https://api.tempo.io/4/worklogs',
                data    = json.dumps(ticket),
                headers = {
                    'Content-type':  'application/json',
                    'Authorization': 'Bearer ' + os.getenv('TEMPO_BEARER_TOKEN')
                }
                )
    # this gives all attributes
    # print(dir(request))
    #
    # if there is a '4' in this, it is probably an error, in which case the json will probably contain an error:
    if '4' in str(request.status_code):
        cprint("Whoops...\n", 'red')
        cprint(f"{request.json()} \n", 'red')

    cprint(ticket, 'green')
    cprint(f'Tempo API response: {request.status_code}\n', 'green')


# issuekey might not be working anymore for 4.0 API
# https://help.tempo.io/planner/latest/tempo-api-version-4-0-vs-version-3-0-a-comparison
