import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

list_rounds = []
list_round_attendances = []
list_total_attendances = []
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

	# find table with border 2; there are Round, Attendance, and Total Attendance

	for table in soup.find_all("table",  attrs={'border' : '2'}):

		all_bs_in_table = table.find_all("b", string=re.compile(r"(?!Finals)")) # anyting BUT Finals

		if len(all_bs_in_table) == 3:  # this is then a typical table covering a round (not finals)

			b_round, b_round_attendance, b_total_attendance = all_bs_in_table

			list_rounds.append(b_round.text.strip().lower())
			list_round_attendances.append(b_round_attendance.next_sibling.strip().lower())
			list_total_attendances.append(b_total_attendance.next_sibling.strip().lower())

	for table in soup.find_all("table",  attrs={'border' : '1'}):

		if len(table.find_all("tr")) == 2:  # else its' a LADDER
			
			team1_tr, team2_tr = table.find_all("tr")
			
			print("team1=",team1_tr.find("a", {"href": re.compile("teams{1}")}).text.strip())
			print("team2=",team2_tr.find("a", {"href": re.compile("teams{1}")}).text.strip())
	
			team1_pts = team1_tr.find("tt").text
			team2_pts = team2_tr.find("tt").text
	
			team1_score = team1_tr.find("td", {'width': "5%"}).text.strip()
			team2_score = team2_tr.find("td", {'width': "5%"}).text.strip()
	
			print("score team 1:", team1_score)

	# ROUNDS; these are of the form <a name="12"></a>

	# for round_anchor in soup.find_all("a", {"name": re.compile("^[0-9]{1}")}):
	# 	list_rounds.append(round_anchor["name"])

	# list_rounds = [ro for ro in list_rounds for _ in range(games_per_round)] 
	#print(list_rounds)

	# #	
	# # TEAMS
	# #

	# for team_anchor in soup.find_all("a", {"href": re.compile("teams{1}")}):
	# 	list_all_teams.append(team_anchor.text)
	
	# # split these into the home and away teams
	# list_team_1 = list_all_teams[::2]
	# list_team_2 = list_all_teams[1::2]

	# #
	# # DATES; typically, Sat 24-Mar-2012 7:20 PM (6:20 PM)
	# # 

	# for dt in soup.find_all(string=re.compile(r'^[A-Z]{1}[a-z]{2}\s+[0-9]{2}')):
	# 	list_dates.append(dt)

	# #
	# # SCORES
	# #

	# for sc_anchor in soup.find_all("td", text = re.compile(r"[0-9]+"), attrs={'width' : '5%'}):
	# 	list_all_scores.append(sc_anchor.text)

	# # like with the teams, split into the scores for the home and away teams
	# list_score_1 = list_all_scores[::2]
	# list_score_2 = list_all_scores[1::2]

	# # VENUE

	# for venue_anchor in soup.find_all("a", {"href": re.compile("venues{1}")}):
	# 	list_venues.append(venue_anchor.text)

	# # ATTENDANCE; <b>Att: </b>34,118 <b>

	# for bes in soup.find_all("b", string=re.compile(r"Att:\s+")):
	# 	list_attendance.append(bes.next_sibling.strip())

	# # FINALS

	# for bes in soup.find_all("b", string=re.compile(r"\s+Final")):
	# 	list_finals.append(bes.text.strip())

	# # note: append finals to the list of rounds when combining data

	# print("collected {} rounds, {} home teams, {} away teams, {} venues, {} finals".format(len(list_rounds), len(list_team_1), len(list_team_2), len(list_venues), len(list_finals)))
	# # combine everything into a zip
	# data = zip(list_rounds + list_finals, list_dates, list_venues, list_team_1, list_score_1, list_team_2, list_score_2, list_attendance)

	# # for match in data:
	# # 	print(match)

	# df = pd.DataFrame(columns = "round date venue team1 score1 team2 score2 attendance".split())
	
	# for i, gm in enumerate(data):
	# 	df.iloc[i] = gm

	# print(df)






