import requests, os, time, json, io, warnings, argparse, sys

import pytz

from datetime import datetime
import pathos.pools as pp 
from crawler_proto import CrawlerProto, ProfileData

class InstagramCrawler(CrawlerProto):

	def __init__(self, results_directory):
		self.results_directory = results_directory + '/instagram/'

	def query(self, query_data):
		"""

		Args:
			target: Username to be queried
		Returns:
			Raw data returned by the crawl of a profile.

		"""
		target = query_data[1]
		since = datetime.strptime(query_data[2], '%y-%m-%d %H:%M:%S')
		until = datetime.strptime(query_data[3], '%y-%m-%d %H:%M:%S')

		while True:
			try:
				profile_data = requests.get('https://instagram.com/{target}/?__a=1'.format(target=target))
			except requests.exceptions.ConnectionError:
				time.sleep(1)

		if not (profile_data.status_code is requests.codes.ok):
			raise ValueError('Profile {target} was not found on Instagram.'.format(target=target))
		profile_json = profile_data.json()

		if profile_json['user']['is_private']:
			raise ValueError("{target} is a private user, whose posts cannot be read.".format(target=target))

		followerCount = profile_json['user']['followed_by']['count']

		postList = []

		for post in profile_json['user']['media']['nodes']:
			post_date = datetime.fromtimestamp(post['date'])
			if post_date > until:
				continue
			elif post_date < since:
				break
			postList.append(post)

		has_next_page = profile_json['user']['media']['page_info']['has_next_page']
		id_next_page = profile_json['user']['media']['page_info']['end_cursor']

		while True:
			while True:
				try:
					new_data = requests.get('https://instagram.com/{target}/?__a=1&max_id={id_next_page}'.format(target=target, id_next_page=id_next_page))
					break
				except requests.exceptions.ConnectionError:
					time.sleep(1)

			if not (new_data.status_code is requests.codes.ok):
				#print('https://instagram.com/{target}/?__a=1&max_id={id_next_page}'.format(target=target, id_next_page=id_next_page), new_data.status_code)
				break
			new_json = new_data.json()
			has_next_page = new_json['user']['media']['page_info']['has_next_page']
			id_next_page = new_json['user']['media']['page_info']['end_cursor']

			if not has_next_page:
				break

			for post in new_json['user']['media']['nodes']:
				post_date = datetime.fromtimestamp(post['date'])
				if post_date > until:
					continue
				elif post_date < since:
					break
				postList.append(post)

		return [query_data, followerCount, postList]


	def format(self, raw_data):
		"""

		Args:
			raw_data: Raw data returned by the crawl of a profile.
		Returns:
			ProfileData tuple of the formatted profile data.

		"""
		target = raw_data[0]
		followerCount = raw_data[1]
		postList = raw_data[2]

		return ProfileData(Artist_Name=target[0], Artist_Login=target[1], File_create_datetime=str(datetime.now()), Follower_Count=followerCount, Posts=postList)

