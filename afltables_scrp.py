"""

SCRAPE AFLTABLES.COM

--- igor k. 01DEC2016 ---

"""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from collections import defaultdict

# choose the range of years you are interested in; the earliest available year is 1897
y_from = 1990
y_to = 2016

"""
choose what format to save data in:
	0 : don't save at all, just show first 10 rdata ows on screen
	1 : save as a table in .CSV 
	2 : save as a JSON file
"""
save_flag = 1

# want to see yearly counts for the retrieved records? 1 for yes

show_yrecs = 1

# sanity check

assert y_from > 1897, ("sorry, there\'s no data for earliest year {} that you\'ve picked." 
						"you may want to choose another year from 1897 and on..".format(y_from))
assert y_to < 2017, ("sorry, there\'s no data for last year {} that you\'ve picked." 
						"you may want to choose another year before 2017..".format(y_to))
assert y_from <= y_to, ("no, this won\'t work. make sure that the earliest year you pick is before or equal to the last year...")

# show this 
print("""-------> scraping afltables.com""")
# lists to store the scraped data
list_rounds = []
list_round_att = []
list_total_att = []
list_team_1 = []
list_team_2 = []
list_score_1 = []
list_score_2 = []
list_dates = []
list_att = []
list_venues = []

# lists to keep quarterly scores
list_q1_team1 = []
list_q2_team1 = []
list_q3_team1 = []
list_q4_team1 = []
list_q5_team1 = []
list_q1_team2 = []
list_q2_team2 = []
list_q3_team2 = []
list_q4_team2 = []
list_q5_team2 = []

# stats per year
statsy = defaultdict(lambda: defaultdict(int))

for year in range(y_from, y_to + 1):
	
	print("downloading data for", year, "...", end="")

	season_line = "http://afltables.com/afl/seas/" + str(year) +".html"
	
	page = requests.get(season_line)
	
	if page.status_code == 200:
		print("ok")
	else:
		print("error {}!".format(year))

	# create a soup object
	soup = BeautifulSoup(page.content, 'html.parser')

	# find table with border 2; there are Round, Attendance, and Total Attendance; alternatively, 
	# the table may be related to finals, which means that there's the word Finals or similar and nothing else

	def is_qualification(tb):

		if (tb.b and 
			(tb.b.string.strip() != "Finals") and 
			(len(tb.find_all("tr")) == 1) and 
				(len(tb.find_all("td")) == 1)):
			return True
		else:
			return False

	def is_match(tb):

		if (len(tb.find_all("tr")) == 2 and
				tb.has_attr("border") and
					 tb["border"] == "1"):
			return True
		else:
			return False

	#
	# is this tag a table that sits right on top of the match result tables
	# 
	def is_round(tb):

		if (tb.has_attr("border") and 
				tb["border"] == "2" and
			 		len(tb.find_all("tr")) == 1 and 
			 			len(tb.find_all("td")) == 2):
			return True
		else:
			return False

	mtb = 0

	for i, this_header_tbl in enumerate(soup.find_all("table")):

		if is_round(this_header_tbl):

			statsy[year]["number_rounds"] += 1
			
			td1, td2 = this_header_tbl.find_all("td")

			this_round = td1.text.strip().lower()

			t2b1, t2b2 = td2.find_all("b")

			list_round_att.append(t2b1.next_sibling.strip().lower())
			list_total_att.append(t2b2.next_sibling.strip().lower())

		if is_match(this_header_tbl):

			
			statsy[year]["number_games"] += 1

			list_rounds.append(this_round)

			team1_tr, team2_tr = this_header_tbl.find_all("tr")
			list_team_1.append(team1_tr.find("a", {"href": re.compile("teams{1}")}).text.strip())
			list_team_2.append(team2_tr.find("a", {"href": re.compile("teams{1}")}).text.strip())
			qscores_t1 = team1_tr.find("tt").text.split()
			qscores_t2 = team2_tr.find("tt").text.split()

			q1t1, q2t1, q3t1, q4t1 = qscores_t1[:4]
			q1t2, q2t2, q3t2, q4t2 = qscores_t2[:4]

			if (len(qscores_t1) == 5) and (len(qscores_t2) == 5):
				q5t1 = qscores_t1[-1][1:-1]
				q5t2 = qscores_t2[-1][1:-1]
			else:
				q5t1 = None
				q5t2 = None

			list_q1_team1.append(q1t1)
			list_q2_team1.append(q2t1)
			list_q3_team1.append(q3t1)
			list_q4_team1.append(q4t1)
			list_q5_team1.append(q5t1)
			list_q1_team2.append(q1t2)
			list_q2_team2.append(q2t2)
			list_q3_team2.append(q3t2)
			list_q4_team2.append(q4t2)
			list_q5_team2.append(q5t2)

			list_score_1.append(team1_tr.find("td", {'width': "5%"}).text.strip())
			list_score_2.append(team2_tr.find("td", {'width': "5%"}).text.strip())
			
			list_venues.append(team1_tr.find("a", {"href": re.compile("venues{1}")}).text.strip())

			tr1td1,tr1td2,tr1td3,tr1td4 = team1_tr.find_all("td")

			list_att.append(tr1td4.b.next_sibling.strip())

			list_dates.append(tr1td4.text.split("Att")[0].strip())

		if is_qualification(this_header_tbl):

			statsy[year]["number_final_rounds"] += 1

			this_round = this_header_tbl.b.text.strip().lower()
			list_round_att.append(None)
			list_total_att.append(None)

# now combine eerything into a zip
data = zip(list_rounds, list_dates, list_team_1, 
				list_q1_team1,list_q2_team1,list_q3_team1,list_q4_team1,list_q5_team1, list_score_1,
				 list_team_2, list_q1_team2,list_q2_team2,list_q3_team2,list_q4_team2, list_q5_team2,
					list_score_2, list_venues, list_att)


# put the data into a pandas data frame
df = pd.DataFrame(columns="round date team1 t1q1 t1q2 t1q3 t1q4 t1q5 t1score team2 t2q1 t2q2 t2q3 t2q4 t2q5 t2score venue attendance".split())

for i, row in enumerate(data):
	df.loc[i] = row

print("successfully retrieved {} results..".format(len(df.index)))

if show_yrecs:
	df_statsy = pd.DataFrame.from_dict(statsy)
	print(df_statsy)

if save_flag == 0:

	print(df.head(10))

elif save_flag == 1:

	if y_from != y_to:
		csv_fl = "scraped_data_from_afltables_yrs_" + str(y_from) + "_to_" + str(y_to) + ".csv"
	else:
		csv_fl = "scraped_data_from_afltables_" + str(y_from) + ".csv"

	df.to_csv(csv_fl, index=False, sep="&")
elif save_flag == 2:

	if y_from != y_to:
		csv_fl = "scraped_data_from_afltables_yrs_" + str(y_from) + "_to_" + str(y_to) + ".json"
	else:
		csv_fl = "scraped_data_from_afltables_" + str(y_from) + ".json"
	df.to_json(csv_fl, orient='records')


print("done. saved the scraped data to file {} in your current directory..".format(csv_fl))






