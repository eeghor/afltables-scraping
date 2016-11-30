import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

list_rounds = []
list_finals = []
list_all_teams = []
list_team_1 = []
list_team_2 = []
list_all_scores = []
list_score_1 = []
list_score_2 = []
list_dates = []
list_attendance = []
list_venues = []

games_per_round = 9

for year in range(2000, 2017):
	
	print("downloading data for", year, "...", end="")

	season_line = "http://afltables.com/afl/seas/" + str(year) +".html"
	
	page = requests.get(season_line)
	
	if page.status_code == 200:
		print("ok")
	else:
		print("something went wrong for year {}!".format(year))

	# create a soup object
	soup = BeautifulSoup(page.content, 'html.parser')

	# ROUNDS; these are of the form <a name="12"></a>

	for round_anchor in soup.find_all("a", {"name": re.compile("^[0-9]{1}")}):
		list_rounds.append(round_anchor["name"])

	list_rounds = [ro for ro in list_rounds for _ in range(games_per_round)] 
	print(list_rounds)

	#	
	# TEAMS
	#

	for team_anchor in soup.find_all("a", {"href": re.compile("teams{1}")}):
		list_all_teams.append(team_anchor.text)
	
	# split these into the home and away teams
	list_team_1 = list_all_teams[::2]
	list_team_2 = list_all_teams[1::2]

	#
	# DATES; typically, Sat 24-Mar-2012 7:20 PM (6:20 PM)
	# 

	for dt in soup.find_all(string=re.compile(r'^[A-Z]{1}[a-z]{2}\s+[0-9]{2}')):
		list_dates.append(dt)

	#
	# SCORES
	#

	for sc_anchor in soup.find_all("td", text = re.compile(r"[0-9]+"), attrs={'width' : '5%'}):
		list_all_scores.append(sc_anchor.text)

	# like with the teams, split into the scores for the home and away teams
	list_score_1 = list_all_scores[::2]
	list_score_2 = list_all_scores[1::2]

	# VENUE

	for venue_anchor in soup.find_all("a", {"href": re.compile("venues{1}")}):
		list_venues.append(venue_anchor.text)

	# ATTENDANCE; <b>Att: </b>34,118 <b>

	for bes in soup.find_all("b", string=re.compile(r"Att:\s+")):
		list_attendance.append(bes.next_sibling.strip())

	# FINALS

	for bes in soup.find_all("b", string=re.compile(r"\s+Final")):
		list_finals.append(bes.text.strip())

	# note: append finals to the list of rounds when combining data

	print("collected {} rounds, {} home teams, {} away teams, {} venues, {} finals".format(len(list_rounds), len(list_team_1), len(list_team_2), len(list_venues), len(list_finals)))
	# combine everything into a zip
	data = zip(list_rounds + list_finals, list_dates, list_venues, list_team_1, list_score_1, list_team_2, list_score_2, list_attendance)

	# for match in data:
	# 	print(match)

	df = pd.DataFrame(columns = "round date venue team1 score1 team2 score2 attendance".split())
	
	for i, gm in enumerate(data):
		df.iloc[i] = gm

	print(df)






