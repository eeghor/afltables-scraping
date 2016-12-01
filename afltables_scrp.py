"""

SCRAPE AFLTABLES.COM

--- igor k. 01DEC2016 ---

"""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# choose the range of years you are interested in; the earliest available year is 1897
y_from = 1998
y_to = 2016

"""
choose what format to save data in:
	0 : don't save at all, just show first 10 rdata ows on screen
	1 : save as a table in .CSV 
"""
save_flag = 1

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

	for tb_round in soup.find_all("table",  attrs={'border' : '2'}):

		# so we start from the first detected table with border=2, which is hopefully describing a round
		# find all <b> in this table; normally, there will be 3 of these and only the Finals tables have one

		all_bs_in_table = tb_round.find_all("b")

		nbs = len(all_bs_in_table)

		if len(all_bs_in_table) in [1,3]:  # if indeed found 3 <b>, then assume this is a round table

			if nbs == 3:

				b_round, b_round_attendance, b_total_attendance = all_bs_in_table
	
				this_round = b_round.text.strip().lower()
				list_round_att.append(b_round_attendance.next_sibling.strip().lower())
				list_total_att.append(b_total_attendance.next_sibling.strip().lower())
			
			elif nbs == 1:

				if len(all_bs_in_table[0].text.split()) > 1:  #  so it's not Finals

					b_round = all_bs_in_table[0]
	
					this_round = b_round.text.strip().lower()
					list_round_att.append(None)
					list_total_att.append(None)

			else:
				continue  # go to the next round table

			# findNext follows an object's next member gathering Tag or NavigableText
			# objects that match the specified criteria:
			
			# so this is the current round table; we want to move on to the next table which is supposed to
			# have border=1 and contain match results

			nxt = tb_round

			not_next_round = 1

			while not_next_round:

				# the below is hopefully a result table:
				nxt = nxt.findNext("table", {"style": "font: 12px Verdana;", "border": "1"})

				# this table would normally have 2 rows..

				if nxt and len(nxt.find_all("tr")) == 2:  #  this should exclude Ladders
	
					list_rounds.append(this_round)
	
					team1_tr, team2_tr = nxt.find_all("tr")
	
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
					list_att.append(team1_tr.find("b").next_sibling.strip())
	
					list_dates.append(team1_tr.find_all("td")[3].text.split("Att")[0].strip())
				else:
					not_next_round = 0

# now combine everything into a zip
data = zip(list_rounds, list_dates, list_team_1, 
				list_q1_team1,list_q2_team1,list_q3_team1,list_q4_team1,list_q5_team1, list_score_1,
				 list_team_2, list_q1_team2,list_q2_team2,list_q3_team2,list_q4_team2, list_q5_team2,
					list_score_2, list_venues, list_att)


# put the data into a pandas data frame
df = pd.DataFrame(columns="round date team1 t1q1 t1q2 t1q3 t1q4 t1q5 t1score team2 t2q1 t2q2 t2q3 t2q4 t2q5 t2score venue attendance".split())

for i, row in enumerate(data):
	df.loc[i] = row
print("successfully retrieved {} results..".format(len(df.index)))

if save_flag == 0:
	print(df.head(10))
elif save_flag == 1:
	csv_fl = "scraped_data_from_afltables_yrs_" + str(y_from) + "_to_" + str(y_to) + ".csv"
	df.to_csv(csv_fl, index=False)
	print("done. saved the scraped data to file {} in your current directory..".format(csv_fl))






