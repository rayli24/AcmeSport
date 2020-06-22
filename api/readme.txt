author: Raylison Ortela
---Code challenge---

Imports:
flask -> as the api framework
requests -> for get the json format
datetime -> for getting the dates from to a specific dates
apscheduler -> for scheduling the job every 10 seconds
pusher -> third party to broadcast an event
atexit -> to shutdown the scheduler
json -> to display json format
jinja2 -> to render the results in the template

Instructions:
1). (THE PROGRAM WILL RUN WITHOUT THIS) Go on www.pusher.com and create an account for free.
    create an app on the dashboard called 'acmeSport'.
	copy the app credentials(App, ID, Key, Secret, Cluster).
	change it with my pusher_client on line 19.
2). Run the python file: python api.py
	by default the start and end dates will be 2020-01-12 to 2020-01-19.
	to search for a different date go to the port link and type:
	/acmesports/startDate as(YYYY-MM-DD)/endDate as(YYYY-MM-DD).
	example: /acmesports/2020-01-16/2020-12-19
3.  The new updates will be printed every 10 seconds in the cli/cmd.

Assumptions:
1). By using pusher in javascript with html script you will be able to
	get updates every 10 seconds on the website.

Decisions made:
1).  The reason requests was used is so that I can make a request to the remote api.
2).  Apscheduler starts a background thread to keep checking for updates every 10 seconds.
3).  Each time the program find data it will collect it and save it into a list named sport_data
4).  I managed to combine the two endpoints by matching the away and home team_id in scoreboard endpoint
	 with team_id in ranking endpoint.
5).  For the event_date I used datetime with strptime to access the date. After I formatted it with strftime
	 to get the desire output. As for how to get just the date I used slice.
6).  I also used slice to get the time.
7).  For the 2 decimal rounding number I used number formatting.
8).  There will be two outputs. One will be displayed in the corresponded port and the other one will be
	 displayed in the cli/cmd. The cli/cmd will keep displaying the new update.
	 This is to prove that the apscheduler/update is working.
9).  Pusher will be used so that it can keep updating the website every time receive_data
	 is being called.
10). disabled auto_reloader in the app.run() to prevent the schedule function from running twice.


