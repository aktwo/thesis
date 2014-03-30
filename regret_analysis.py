import json
from datetime import datetime, date, timedelta
import collections
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

###################################################
### Helper functions to process input JSON file ###
###################################################
def conversation_date(convo):
  return date.fromtimestamp(convo['startTime']/1000.0)
def first_user(convo):
  return convo['userID1']
def second_user(convo):
  return convo['userID2']
def users(convo):
  return [first_user(convo), second_user(convo)]
def first_user_clicked(convo):
  return convo['user1Clicked']
def second_user_clicked(convo):
  return convo['user2Clicked']
def fb_match_occurred(convo):
  return first_user_clicked(convo) and second_user_clicked(convo)
def first_user_messages_sent(convo):
  return convo['user1MessagesSent']
def second_user_messages_sent(convo):
  return convo['user2MessagesSent']
def first_user_disconnected(convo):
  return first_user_messages_sent(convo) == 0
def second_user_disconnected(convo):
  return second_user_messages_sent(convo) == 0
def no_immediate_disconnect_occurred(convo):
  return not(first_user_disconnected(convo) and second_user_disconnected(convo))

#############################################################
### Helper functions to extract data from input JSON file ###
#############################################################

# Returns list of tuples of form (date, {wins: 0, plays: 0})
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

# Returns list of tuples of form (date, {wins: 0, plays: 0})
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

# Returns list of cumulative regret values with respect to the win_metric
def cumulative_regret(data, win_metric):
  def reduce_function(total, play):
    try:
      curr_wins = total[-1][1]
      curr_plays = total[-1][2]
    except:
      curr_wins = 0
      curr_plays = 0
    total.append((play, curr_wins + play, curr_plays + 1))
    return total
  results = reduce(reduce_function, map(lambda convo: win_metric(convo), data), [])
  optimal_win_ratio = results[-1][1]/float(results[-1][2])
  return map(lambda (result, wins, plays): (optimal_win_ratio * plays) - wins, results)

# Returns ordered dictionary of form {date: win_ratio}
def win_ratio(win_play_data, threshold=0):
  output = {}
  for data_point in win_play_data:
    date = data_point[0]
    wins = data_point[1]['wins']
    plays = data_point[1]['plays']
    if plays >= threshold:
      output[date] = wins/plays
  return collections.OrderedDict(sorted(output.items()))

# Generates an list where the (i-1)-th index represents
# the average value of the user1/2_metric for all the users
# on their i-th play conditional on having played i or more times.
# For example, a result of 0.5 in the list index of 9 would mean
# that for all users who played 10 or more times, the average value
# of the metric on their 10th play was 0.5.
def generate_user_data(data, user1_metric, user2_metric):
  user_data = {}
  for convo in data:
    if first_user(convo) in user_data:
      user_data[first_user(convo)].append(user1_metric(convo))
    else:
      user_data[first_user(convo)] = [user1_metric(convo)]
    if second_user(convo) in user_data:
      user_data[second_user(convo)].append(user2_metric(convo))
    else:
      user_data[second_user(convo)] = [user2_metric(convo)]
  user_aggregate = []
  for user in user_data:
    user_aggregate.append(user_data[user])
  user_aggregate = map(None, *user_aggregate)
  output = []
  for iteration in user_aggregate:
    num_successes = reduce(lambda a, b: a + b if b != None else a, iteration, 0.0)
    num_trials = reduce(lambda a, b: a + 1 if b != None else a, iteration, 0)
    output.append(num_successes/num_trials)
  return output

# Given data in the form of a list of values, return an list containing
# the simple moving average with a specified window_size
def get_moving_average(data, window_size):
  output = [data[0]]
  for i in range(1, window_size-1):
    output.append(sum(data[0:i+1])/float(i+1))
  for i in range(window_size, len(data)+1):
    output.append(sum(data[i-window_size:i])/float(window_size))
  return output

#######################################################
### Helper functions to format and display the data ###
#######################################################

# Takes in ordered dictionary d and saves it as name
def save_plot(d, title, xlabel='Date', ylabel='Metric'):
  x = []
  y = []
  for key in d:
    x.append(key)
    y.append(d[key])
  fig, ax = plt.subplots()
  fig.suptitle(title)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  plt.plot(x, y)
  fig.autofmt_xdate()
  fig.savefig(title+'.jpg')

####################################################################
### Commands to use the above functions to perform data analysis ###
####################################################################

# Load the JSON data
data = json.load(open('ta_data.json', 'r'))

# # FB win ratio, both daily and cumulatively
# fb_daily_wins_and_plays = daily_win_play_data(data, fb_match_occurred)
# fb_cumulative_wins_and_plays = cumulative_win_play_data(data, fb_match_occurred)
# fb_daily_win_ratio = win_ratio(fb_daily_wins_and_plays, threshold=20)
# fb_cumulative_win_ratio = win_ratio(fb_cumulative_wins_and_plays)
# save_plot(fb_daily_win_ratio, 'Daily TA De-Anonymization', ylabel='Percent of participants opting for de-anonymization')
# save_plot(fb_cumulative_win_ratio, 'Cumulative TA De-Anonymization', ylabel='Percent of participants opting for de-anonymization')

# Disconnect win ratio

# Cumulative regret analysis for FB

# Per user data analysis
fb_user_data = generate_user_data(data, first_user_clicked, second_user_clicked)
disconnect_user_data = generate_user_data(data, first_user_disconnected, second_user_disconnected)
user_messages_sent = generate_user_data(data, first_user_messages_sent, second_user_messages_sent)
plt.plot(user_messages_sent)
moving_average = get_moving_average(user_messages_sent, 20)
plt.plot(moving_average, 'r--')
plt.show()


