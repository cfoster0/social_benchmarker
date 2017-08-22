import requests, sys, os, time, json, warnings, argparse, sys

from datetime import datetime
import pathos.pools as pp 
from crawler_proto import CrawlerProto, ProfileData


class InstagramCrawler(CrawlerProto):

	def __init__(self, results_directory):
		self.results_directory = results_directory + '/instagram/'
		self._session = requests.Session()

	def query(self, query_data):

		"""
		Arguments:
			query_data: Metadata relating to the profile to be queried.
		Returns:
			List of raw data returned by the crawl of a profile.
		"""

		def getRequests(url):

			"""
			Arguments:
				url: The URL of the API request to be made, including the token.
			Returns:
				requests_result: The result of the (presumably successful)
					HTTP request that was made.
			"""
			
			requests_result = None
			attempts = 5
			for n in range(attempts, 0, -1):
				try:
					requests_result = self._session.get(url)
					break
				except requests.exceptions.ConnectionError:
					print('Request failed... will try {n} more time(s).'.format(n=n))
					time.sleep(4)
			if (requests_result is None) or (requests_result.status_code is not requests.codes.ok):
				raise ValueError('Profile query failed, as requests to {url} were not successful.'.format(url=url))
			return requests_result

		def getFollowers(profile):

			"""
			Arguments:
				profile: The result of calling the API for a profile.
			Returns:
				The follower count for that profile.
			"""

			return profile['user']['followed_by']['count']

		def getPosts(profile):

			"""
			Arguments:
				profile: The result of calling the API for a profile.
			Returns:
				The list of posts for that profile.
			"""

			return profile['user']['media']['nodes']

		def getSelectPosts(profile, start, end):

			"""
			Arguments:
				profile: The result of calling the API for a profile.
				start: The datetime of the start of the period of interest.
				end: The datetime of the end of the period of interest.
			Returns:
				post_list: The posts from a profile within that selected
					time frame.
			"""

			post_list = []
			for post in getPosts(profile):
				post_date = datetime.fromtimestamp(post['date'])
				if post_date > until:
					continue
				elif post_date < since:
					break
				post_list.append(parsePost(post))
			return post_list

		def getNextPage(profile):

			"""
			Arguments:
				profile: The result of calling the API for a profile.
			Returns:
				Either the next page of profile data or a None object,
					if the data cannot be accessed.
			"""

			if profile['user']['media']['page_info']['has_next_page']:
				return profile['user']['media']['page_info']['end_cursor']
			else:
				return None

		def parsePost(post):

			"""
			Arguments:
				post: The result of calling the API for a post.
			Returns:
				post_data: A formatted dictionary of the relevant
					data on a post.
			"""

			post_data = {}
			post_data['id'] = post['code']
			if 'caption' in post:
				post_data['caption'] = post['caption']
			else:
				post_data['caption'] = ''
			post_data['is_video'] = post['is_video']
			post_data['likes'] = post['likes']['count']
			post_data['comments'] = post['comments']['count']
			return post_data

		#####

		target = query_data[1]
		since = datetime.strptime(query_data[2], '%y-%m-%d %H:%M:%S')
		until = datetime.strptime(query_data[3], '%y-%m-%d %H:%M:%S')

		try:
			profile_data = getRequests('https://instagram.com/{target}/?__a=1'.format(target=target))

			profile_json = profile_data.json()

			if profile_json['user']['is_private']:
				raise ValueError("{target} is a private user, whose posts cannot be read.".format(target=target))

			followerCount = getFollowers(profile_json)
			postList = []
			postList.extend(getSelectPosts(profile_json, since, until))

			next_page = getNextPage(profile_json)

			while True:
				if next_page is None:
					break

				new_data = getRequests('https://instagram.com/{target}/?__a=1&max_id={id_next_page}'.format(target=target, id_next_page=next_page))
				new_json = new_data.json()

				postList.extend(getSelectPosts(new_json, since, until))

				next_page = getNextPage(new_json)

			return [query_data, followerCount, postList]

		except ValueError:
			return [query_data, 0, []]


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

