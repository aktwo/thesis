import json
from datetime import datetime, date
import collections

def conversation_date(convo):
  return date.fromtimestamp(convo['startTime']/1000.0)

def users(convo):
  return [convo['userID1'], convo['userID2']]

def fb_match_occurred(convo):
  return convo['user1Clicked'] and convo['user2Clicked']

def no_immediate_disconnect_occurred(convo):
  return not((convo['user1MessagesSent'] == 0) and (convo['user2MessagesSent'] == 0))

def get_time_series(regret_data, threshold):
  output = {}
  for date in regret_data:
    if regret_data[date]['plays'] > threshold:
      output[date] = regret_data[date]['wins']/regret_data[date]['plays']
  return collections.OrderedDict(sorted(output.items()))

def generate_regret_data(data, metric):
  regret_data = {}
  for convo in data:
    date = conversation_date(convo)
    if date in regret_data: 
      regret_data[date]['wins'] += metric(convo)
      regret_data[date]['plays'] += 1.0
    else:
      regret_data[date] = {'wins': 0.0 + metric(convo), 'plays': 1.0}
  return regret_data

data = json.load(open('ta_data.json', 'r'))
# fb_regret_time_series = generate_regret_data(data, fb_match_occurred)
# disconnect_regret_time_series = generate_regret_data(data, no_immediate_disconnect_occurred)

# print get_time_series(fb_regret_time_series, 50)
# print "-"*50
# print get_time_series(disconnect_regret_time_series, 50)

def generate_user_data(data, metric):
  user_data = {}
  for convo in data:
    for user in users(convo):
      if user in user_data:
        user_data[user].append(metric(convo))
      else:
        user_data[user] = [metric(convo)]
  return user_data

fb_user_data = generate_user_data(data, fb_match_occurred)

