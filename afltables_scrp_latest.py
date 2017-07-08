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
import boto3
import schedule

class ScoreCollector(object):

	def __init__(self):

		self.list_rounds = []
		self.list_team_1 = []
		self.list_team_2 = []
		self.list_score_1 = []
		self.list_score_2 = []
		self.list_dates = []
		self.list_att = []
		self.list_venues = []

		self.DATE_FORMAT = r'\b\d{2}-\w{3}-\d{4}\b'

		# figure out what is today's date
		self.now = datetime.now()
		year, month, day = self.now.year, self.now.month, self.now.day

		# date format on the site is 06-Jun-2017
		ml = {i: m for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
		self.date_now = "-".join(["{:02d}".format(day), ml[month], str(year)])
		self.RESULT_FILE_NAME = "afl-latest-" + self.date_now + ".csv"

		self.SEASON_LINE = "http://afltables.com/afl/seas/" + str(self.now.year) +".html"

	def _get_season_page(self):
		try:
			page = requests.get(self.SEASON_LINE)
		except:
			print("[ERROR]: couldn't get the season page...")
			sys.exit(0)
		# create a soup object
		self.soup = BeautifulSoup(page.content, 'html.parser')

		return self

	def cd(self, tag_name, width_value):
		"""
		wrapper to pass arguments to a function that looks for tags with
		certain width attrs
		"""
		def wrapper(tag):
			if (tag.name == tag_name) and ("width" in tag.attrs):
					if tag.attrs["width"] == width_value:
						for l in tag.stripped_strings:
							if l:
								if re.compile(self.DATE_FORMAT).search(l):  # r means all escape codes will be ignored
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

	def nearest_date(self):
		"""
		find a past date closest to today on the results page
		"""
		date_list = []

		tbls = self.soup.find_all(self.cd("td", "85%"))
		for td in self.soup.find_all(self.cd("td", "85%")):  # returns a list
			for l in td.stripped_strings:
				r = re.compile(self.DATE_FORMAT).search(l)
				if r:
					date_list.append(datetime.strptime(r.group(0), "%d-%b-%Y"))
		for tb in self.soup.find_all(self.cd("table", "100%")):  # returns a list
			r = re.compile(self.DATE_FORMAT).search(tb.text)
			if r:
				date_list.append(datetime.strptime(r.group(0), "%d-%b-%Y"))

		return min([dt for dt in date_list if self.now > dt], key=lambda _: self.now - _).strftime("%d-%b-%Y")

	def _collect_match_info_from_tds(self, tag):
		"""
		extract data from a match results table
		"""
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

	def search_for_results(self):

		# print("today is {}".format(self.date_now))

		nearest = self.nearest_date()
		# print("latest round played on {}".format(nearest))

		ROUND_RESULTS_FOUND = False

		for td in self.soup.find_all(self.cd("td", "85%")):

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
					self.list_rounds.append(this_round)
					dt, team1, team1score, team2, team2score, venue, att = self._collect_match_info_from_tds(table)
					self.list_dates.append(dt)
					self.list_team_1.append(team1)
					self.list_score_1.append(team1score)
					self.list_team_2.append(team2)
					self.list_score_2.append(team2score)
					self.list_venues.append(venue)
					self.list_att.append(att)

				break  # no need ot search more tds

		if not ROUND_RESULTS_FOUND:

			print("[WARNING]: couldn't find any regular rounds, checking finals...")

			for tb in self.soup.find_all(self.cd("table", "100%")):
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

					dt, team1, team1score, team2, team2score, venue, att = self._collect_match_info_from_tds(tb)
					self.list_rounds.append(this_round)
					self.list_dates.append(dt)
					self.list_team_1.append(team1)
					self.list_score_1.append(team1score)
					self.list_team_2.append(team2)
					self.list_score_2.append(team2score)
					self.list_venues.append(venue)
					self.list_att.append(att)

					break

		return self

	def save_as_csv(self):

		data = (pd.DataFrame({"round" : self.list_rounds, "date": self.list_dates,
							"team1": self.list_team_1, "team1selfore": self.list_score_1,
							"team2": self.list_team_2, "team2selfore": self.list_score_2,
							"venue": self.list_venues, "attendance": self.list_att}, 
							columns=["round date team1 team1selfore team2 team2selfore venue attendance"
							.split()]).to_csv(self.RESULT_FILE_NAME, sep="&", index=False))
		return self

	def send_to_s3(self):

		s3 = boto3.resource('s3')
		s3.meta.client.upload_file(self.RESULT_FILE_NAME,
		'tega-uploads', "Igor/afl-latest/" + self.RESULT_FILE_NAME)

		return self

if __name__ == "__main__":

	def job():
		(ScoreCollector()
			._get_season_page()
			.search_for_results()
			.save_as_csv()
			.send_to_s3())

	schedule.every().saturday.at("22:30").do(job)

	while True:
		schedule.run_pending()


