import json
from datetime import datetime, date, timedelta
import collections
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def conversation_date(convo):
  return date.fromtimestamp(convo['startTime']/1000.0)

def users(convo):
  return [convo['userID1'], convo['userID2']]

def fb_match_occurred(convo):
  return convo['user1Clicked'] and convo['user2Clicked']

def no_immediate_disconnect_occurred(convo):
  return not((convo['user1MessagesSent'] == 0) and (convo['user2MessagesSent'] == 0))

def daily_win_play_data(data, win_metric):
  regret_data = {}
  for convo in data:
    date = conversation_date(convo)
    if date in regret_data: 
      regret_data[date]['wins'] += win_metric(convo)
      regret_data[date]['plays'] += 1.0
    else:
      regret_data[date] = {'wins': 0.0 + win_metric(convo), 'plays': 1.0}
  return sorted(regret_data.items())

def cumulative_win_play_data(data, win_metric):
  win_play_data = daily_win_play_data(data, win_metric)
  output = {}
  output[win_play_data[0][0]] = win_play_data[0][1]
  for i in range(1, len(win_play_data)):
    curr_data_point = win_play_data[i]
    curr_date = curr_data_point[0]
    curr_wins = curr_data_point[1]['wins']
    curr_plays = curr_data_point[1]['plays']
    prev_date = win_play_data[i-1][0]
    prev_wins = output[prev_date]['wins']
    prev_plays = output[prev_date]['plays']
    output[curr_date] = {'wins': curr_wins + prev_wins, 'plays': curr_plays + prev_plays}
  return sorted(output.items())

def win_ratio(win_play_data, threshold=0):
  output = {}
  for data_point in win_play_data:
    date = data_point[0]
    wins = data_point[1]['wins']
    plays = data_point[1]['plays']
    if plays >= threshold:
      output[date] = wins/plays
  return collections.OrderedDict(sorted(output.items()))



def plot(d, title='title', xlabel='xlabel', ylabel='ylabel', name='test.jpg'):
  x = []
  y = []
  for key in d:
    x.append(key)
    y.append(d[key])
  fig = plt.figure()
  fig.suptitle(title)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  plt.plot(x, y)
  plt.show()

data = json.load(open('ta_data.json', 'r'))
fb_daily_wins_and_plays = daily_win_play_data(data, fb_match_occurred)
fb_cumulative_wins_and_plays = cumulative_win_play_data(data, fb_match_occurred)

fb_daily_win_ratio = win_ratio(fb_daily_wins_and_plays, threshold=20)
fb_cumulative_win_ratio = win_ratio(fb_cumulative_wins_and_plays, threshold=20)

plot(fb_daily_win_ratio)
plot(fb_cumulative_win_ratio)

# plot(disconnect_regret_time_series)
# print disconnect_regret_time_series

def generate_user_data(data, metric):
  user_data = {}
  for convo in data:
    for user in users(convo):
      if user in user_data:
        user_data[user].append(metric(convo))
      else:
        user_data[user] = [metric(convo)]
  return user_data

# fb_user_data = generate_user_data(data, fb_match_occurred)

