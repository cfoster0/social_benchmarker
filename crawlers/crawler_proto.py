import os, sys, time, json, csv, io
from collections import namedtuple
from abc import ABCMeta
from abc import abstractmethod

ProfileData = namedtuple('ProfileData', ['Artist_Name', 'Artist_Login', 'File_create_datetime', 'Follower_Count', 'Posts'])

class CrawlerProto(object):

	def __init__(self, crawl_type, results_directory):
		__metaclass__ = ABCMeta
		"""
		
		Args:
			crawl_type: What type of crawl should be performed.
			results_directory: Where the results should be saved to.
		Returns:

		"""
		self.crawl_type = crawl_type
		self.results_directory = results_directory

	#def set_times(self, start, end):
	#	self.start = start
	#	self.end = end

	def set_profiles(self, profiles_file_name):
		self.profiles_file_name = profiles_file_name
		self.download_if_not_present(self.profiles_file_name)	

	@abstractmethod
	def query(self, query_data):
		"""

		Args:
			query_data: Terms of the query
		Returns:
			Raw data returned by the crawl of a profile.

		"""
		pass

	@abstractmethod
	def format(self, user_data):
		"""

		Args:
			user_data: Raw data returned by the crawl of a profile.
		Returns:
			ProfileData tuple of the formatted profile data.

		"""
		pass

	def __iter__(self):
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
		self.profiles = {}
		with open(profiles_file_name, 'r') as csvfile: 
			reader = csv.reader(csvfile, delimiter=',', quotechar = '|')
			for row in reader:
				artistName = row[0]
				target = row[1]
				startDateTime = row[2]
				endDateTime = row[3]
				self.profiles[target] = [artistName, target, startDateTime, endDateTime]

	def save(self, data):
		formatted_data = self.format(data)._asdict()

		save_location = self.results_directory + formatted_data['Artist_Name'] +'.json'

		#with io.open(save_location, 'w', encoding = "utf-8") as f:
		with open(save_location, 'w') as f:
			json.dump(formatted_data, f, indent = 4, ensure_ascii=False)

