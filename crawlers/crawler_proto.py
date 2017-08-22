import os, sys, time, json, csv
from collections import namedtuple
from abc import ABCMeta
from abc import abstractmethod

ProfileData = namedtuple('ProfileData', ['Artist_Name', 'Artist_Login', 'File_create_datetime', 'Follower_Count', 'Posts'])

class CrawlerProto(object):

	def __init__(self, crawl_type, results_directory):
		__metaclass__ = ABCMeta

		"""
		Arguments:
			crawl_type: What type of crawl should be performed.
			results_directory: Where the results should be saved to.
		"""

		self.crawl_type = crawl_type
		self.results_directory = results_directory

	def set_profiles(self, profiles_file_name):
		
		"""
		Arguments:
			profiles_file_name: The file where the profile metadata is stored.
		"""

		self.profiles = {}
		self.profiles_file_name = profiles_file_name
		self.download_if_not_present(self.profiles_file_name)	

	@abstractmethod
	def query(self, query_data):
		
		"""
		Arguments:
			query_data: Metadata relating to the profile to be queried.
		Returns:
			List of raw data returned by the crawl of a profile.
		"""

		pass

	@abstractmethod
	def format(self, user_data):
		
		"""
		Arguments:
			raw_data: Raw data list returned by the crawl of a profile (from the query function).
		Returns:
			ProfileData tuple of the formatted profile data.
		"""

		pass

	def __iter__(self):

		# Allows one to iterate over the crawler using the "for x in y" syntax

		for key in self.list_keys():
			yield self.profiles[key]

		raise StopIteration()

	def list_keys(self):
		if self.profiles is None:
			if self.profiles_file_name is None:
				raise Exception('No profile list provided.')
			else:
				self.profiles = self.download_if_not_present(self.profiles_file_name)
		else:
			return self.profiles.keys()

	def download_if_not_present(self, profiles_file_name):

		"""
		Arguments:
			profiles_file_name: The file where the profile metadata is stored.
		"""

		self.profiles = {}
		with open(profiles_file_name, 'r') as csvfile: 
			reader = csv.reader(csvfile, delimiter=',', quotechar = '|')
			for row in reader:
				if row[0] in ['Genre', 'Genres', 'Genre(s)', 'GENRE', 'GENRES', 'GENRE(S)']:
					continue
				genres = row[0]
				artistName = row[1]
				target = row[2]
				startDateTime = row[3]
				endDateTime = row[4]
				self.profiles[target] = [artistName, target, startDateTime, endDateTime]

	def save(self, data):

		"""
		Arguments:
			data: Profile data to be saved to disk.
		"""

		formatted_data = self.format(data)._asdict()

		save_location = self.results_directory + formatted_data['Artist_Name'] +'.json'

		with open(save_location, 'w') as f:
			json.dump(formatted_data, f, indent = 4, ensure_ascii=False)

