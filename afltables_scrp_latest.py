"""

SCRAPE THE LATEST ROUND RESULTS from AFLTABLES.COM

--- igor k. 06JUL2017 ---

"""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sys
from datetime import datetime

# show this 
print("collecting latest results from afltables.com...")
# lists to store the scraped data
list_rounds = []
list_team_1 = []
list_team_2 = []
list_score_1 = []
list_score_2 = []
list_dates = []
list_att = []
list_venues = []

# figure out what is today's date
now = datetime.now()
year, month, day = now.year, now.month, now.day

# date format on the site is 06-Jun-2017
month_num_to_letter = {i: m for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
this_month = "-".join(["{:02d}".format(day), month_num_to_letter[month], str(year)])

season_line = "http://afltables.com/afl/seas/" + str(now.year) +".html"

try:
	page = requests.get(season_line)
except:
	print("[ERROR]: couldn't get the season page...")
	sys.exit(0)


DATE_FORMAT = r'\b\d{2}-\w{3}-\d{4}\b'

# create a soup object
soup = BeautifulSoup(page.content, 'html.parser')

def cd(tag_name, width_value):
	def wrapper(tag):
		if (tag.name == tag_name) and ("width" in tag.attrs):
				if tag.attrs["width"] == width_value:
					for l in tag.stripped_strings:
						if l:
							if re.compile(DATE_FORMAT).search(l):  # r means all escape codes will be ignored
								return True
							else:
								continue  # to the next string
						else:
							continue  # move on as the string is empty
						return False  # if got to here, nothing has been found
				else:
					return False
		else:
			return False
	return wrapper

def nearest_date():

	date_list = []
	tbls = soup.find_all(cd("td", "85%"))
	for td in soup.find_all(cd("td", "85%")):  # returns a list
		for l in td.stripped_strings:
			r = re.compile(DATE_FORMAT).search(l)
			if r:
				date_list.append(datetime.strptime(r.group(0), "%d-%b-%Y"))
	for tb in soup.find_all(cd("table", "100%")):  # returns a list
		r = re.compile(DATE_FORMAT).search(tb.text)
		if r:
			date_list.append(datetime.strptime(r.group(0), "%d-%b-%Y"))

	return min([dt for dt in date_list if now > dt], key=lambda _: now - _).strftime("%d-%b-%Y")

def collect_match_info_from_tds(tag):

	for i, c in enumerate(tag.find_all("td")):
		if i == 0:
			team1 = c.text.strip()
		elif i == 1:
			# quarter scores here, we don't need them
			pass
		elif i == 2:
			team1score = c.text.strip().lower()
		elif i == 3:
			venue = c.text.split("Venue:")[-1].strip()
			search_attend = re.compile(r'Att:\s\d+,\d+').search(c.text)
			att = search_attend.group(0).split(":")[-1].strip() if search_attend else ''
			if not (('AM' in c.text) or ('PM' in c.text)):
				if ":" in c.text:
					dt = " ".join(c.text.split(":")[0].split()[:2]).strip()
				else:
					dt = ''
			else:
				dt = c.text.split("Att:")[0].strip()
		elif i == 4:
			team2 = c.text.strip()
		elif i == 5:
			# quarter scores here, we don't need them
			pass
		elif i == 6:
			team2score = c.text.strip().lower()
		elif i == 7:
				pass
	return (dt, team1, team1score, team2, team2score, venue, att)

print("today is {}".format(this_month))

nearest = nearest_date()
print("latest round played on {}".format(nearest))

ROUND_RESULTS_FOUND = False

for td in soup.find_all(cd("td", "85%")):

	if re.compile(nearest).search(td.text):

		ROUND_RESULTS_FOUND = True

		# find what round it is
		this_round = ''
		for p in td.parents:
			if p.name == "table":
				for s in p.previous_siblings:
					if s.name == "table":
						search_round = re.compile(r'\bRound\s+\d+\b').search(s.text)
						if search_round:
							this_round = search_round.group(0).lower()
		if not this_round:
			print("[WARNING]: can't find which round was the latest...")

		for table in td.find_all("table"):   # 1 table = 1 match
			list_rounds.append(this_round)
			dt, team1, team1score, team2, team2score, venue, att = collect_match_info_from_tds(table)
			list_dates.append(dt)
			list_team_1.append(team1)
			list_score_1.append(team1score)
			list_team_2.append(team2)
			list_score_2.append(team2score)
			list_venues.append(venue)
			list_att.append(att)

		break  # no need ot search more tds

if not ROUND_RESULTS_FOUND:

	print("[WARNING]: couldn't find any regular rounds, checking finals...")

	for tb in soup.find_all(cd("table", "100%")):
		if re.compile(nearest).search(tb.text):
			# have the right table
			ROUND_RESULTS_FOUND = True
			# find what round it is
			try:
				this_round = tb.previous_sibling.previous_sibling.text.strip().lower()
			except:
				this_round = ''
			if not this_round:
				print("[WARNING]: can't find any finals round...")
			else:
				print(this_round)

			dt, team1, team1score, team2, team2score, venue, att = collect_match_info_from_tds(tb)
			list_rounds.append(this_round)
			list_dates.append(dt)
			list_team_1.append(team1)
			list_score_1.append(team1score)
			list_team_2.append(team2)
			list_score_2.append(team2score)
			list_venues.append(venue)
			list_att.append(att)

			break

# now combine eerything into a zip
data = zip(list_rounds, list_dates, list_team_1,
				 list_team_2, list_score_2, list_venues, list_att)
for d in data:
	print(d)
