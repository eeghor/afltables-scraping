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
match_round_dict = {}
match_round = []


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

	for tb_round in soup.find_all("table",  attrs={'border' : '2'}):

		all_bs_in_table = tb_round.find_all("b", string=re.compile(r"(?!Finals)")) # anyting BUT Finals

		if len(all_bs_in_table) == 3:  # this is then a typical table covering a round (not finals)

			b_round, b_round_attendance, b_total_attendance = all_bs_in_table

			print("**************************")

			list_rounds.append(b_round.text.strip().lower())
			list_round_attendances.append(b_round_attendance.next_sibling.strip().lower())
			list_total_attendances.append(b_total_attendance.next_sibling.strip().lower())

			# findNext follows an object's next member gathering Tag or NavigableText
			# objects that match the specified criteria:
			
			tb_match = tb_round.findNext("table", attrs={'border' : '1'})

			if len(tb_match.find_all("tr")) == 2:

				team1_tr, team2_tr = tb_match.find_all("tr")
				# print("team1=",team1_tr.find("a", {"href": re.compile("teams{1}")}).text.strip())
				# print("team2=",team2_tr.find("a", {"href": re.compile("teams{1}")}).text.strip())
				# team1_pts = team1_tr.find("tt").text
				team2_pts = team2_tr.find("tt").text

				team1_score = team1_tr.find("td", {'width': "5%"}).text.strip()
				team2_score = team2_tr.find("td", {'width': "5%"}).text.strip()
				
				venue = team1_tr.find("a", {"href": re.compile("venues{1}")}).text.strip()
				attendance = team1_tr.find("b").next_sibling.strip()

				date_time = team1_tr.find_all("td")[3].text.split("Att")[0]

	

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






