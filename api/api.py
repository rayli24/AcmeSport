#Author: Raylison Ortela

from flask import Flask
import requests
from datetime import datetime,timedelta,date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pusher import Pusher
import atexit
import json
from jinja2 import Template


class Month:
    static_start = '2020-01-12'
    static_end = '2020-01-19'

app = Flask(__name__)
app.config["DEBUG"] = True

# place your pusher info here
pusher_client = Pusher(
  app_id='1019970',
  key='b03b7db0667763766a13',
  secret='47600b79054f686ad1bb',
  cluster='us2',
  ssl=True
)

@app.route('/', methods=['GET'])
def home():
    return "<h1>List of NFL teams<h1>"


@app.route('/acmesports/<starts>/<ends>', methods=['GET'])
def retrieve_data(starts,ends):
    if starts != Month.static_start or ends != Month.static_end:
        scheduler.modify_job('nfl_job_id',args=[starts,ends]) # update the job
        Month.static_start = starts
        Month.static_end = ends
    start = str(Month.static_start)
    end = str(Month.static_end)
    start_date = start.split('-')
    end_date = end.split('-')
    for i in range(3):
        start_date[i] = int(start_date[i])
        end_date[i] = int(end_date[i])
    start_date = date(start_date[0], start_date[1], start_date[2])
    end_date = date(end_date[0], end_date[1], end_date[2])

    sport_data = [] # storage for final json data
    rs = requestscoreboard(start_date,end_date)
    rr = requestranking()
    event_dates = [] # store the event dates
    for single_date in daterange(start_date, end_date):
        event_dates.append(f'{single_date}')

    for day in event_dates:
        for data in rs['results'][day]:
            for info in rs['results'][day][data]:
                num = str(info)
                number = ''
                for j in range(len(num)):
                    if num[j] != "'":
                        number += num[j]
                    else:
                        break

                away_id = rs['results'][day][data][number]['away_team_id']
                home_id = rs['results'][day][data][number]['home_team_id']
                away_index = getid(rr, away_id)
                home_index = getid(rr, home_id)

                game_data = {
                    'event_id': rs['results'][day][data][number]['event_id'],
                    'event_date': datetime.strptime(rs['results'][day]['data'][number]['event_date'][:10], '%Y-%m-%d').strftime('%d-%m-%Y'),
                    'event_time': rs['results'][day][data][number]['event_date'][11:16],
                    'away_team_id': rs['results'][day][data][number]['away_team_id'],
                    'away_nickname': rs['results'][day][data][number]['away_nick_name'],
                    'away_city': rs['results'][day][data][number]['away_city'],
                    'away_rank': rr['results'][data][away_index]['rank'],
                    'away_rank_points': '{:.2f}'.format(float(rr['results'][data][away_index]['adjusted_points'])),
                    'home_team_id': rs['results'][day][data][number]['home_team_id'],
                    'home_nickname': rs['results'][day][data][number]['home_nick_name'],
                    'home_city': rs['results'][day][data][number]['home_city'],
                    'home_rank': rr['results'][data][home_index]['rank'],
                    'home_rank_points': '{:.2f}'.format(float(rr['results'][data][home_index]['adjusted_points'])),
                 }

                sport_data.append(game_data)
            break
    printed_result = f'\nfor the date range {start} to {end}: \n{json.dumps(sport_data,indent=2)}'
    status = f'for the date range {start} to {end}:'
    
    # pusher_client.trigger() would be called in the javascript to be used in the html script
    pusher_client.trigger('acmeSport', 'data-updated', sport_data) #trigger broadcast event
    print(printed_result)
    template = Template('''
    <p>{{status}}</p>
    <pre>{{sport_data|tojson(indent=2)}}</pre>
    ''')
    return template.render(status=status, sport_data=sport_data)


# method:      requestscoreboard
# description: this method takes a start and an end date to pass in to the url.
#              It will call a get request and format it in json.
# parameters:  'str: start', 'str: end'
# return:      json format
def requestscoreboard(start,end):
    url = 'https://delivery.chalk247.com/scoreboard/NFL/{}/{}.json?api_key=74db8efa2a6db279393b433d97c2bc843f8e32b0'
    response = requests.get(url.format(start, end)).json()
    return response

# method:      requestranking
# description: this method get a request from the provided url and format it in json.
# parameters:  None
# return:      json format    
def requestranking():
    url ='https://delivery.chalk247.com/team_rankings/NFL.json?api_key=74db8efa2a6db279393b433d97c2bc843f8e32b0'
    response = requests.get(url).json()
    return response

# method:      getid
# description: this method finds the matching between both end points.
# parameters:  'int: ranking', 'int: team_id'
# return:      integer   
def getid(ranking, team_id):
        index = 0 
        for id in ranking['results']['data']:
            if team_id == id['team_id']:
                break
            index += 1
        return index

# method:      daterange
# description: this method gets all the dates from the start date to the end date.
# parameters:  'str: start_date', 'str: end_date'
# return:      dates  
def daterange(start_date,end_date):
        for num in range(int ((end_date -start_date).days)+1):
            yield start_date + timedelta(num)


scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=retrieve_data,
    trigger=IntervalTrigger(seconds=10),
    id='nfl_job_id',
    args = [Month.static_start,Month.static_end],
    replace_existing=True)
    
atexit.register(lambda: scheduler.shutdown())
app.run(debug=True, use_reloader=False)