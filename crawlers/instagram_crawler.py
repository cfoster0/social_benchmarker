import requests, os, time, json, io, warnings, argparse, sys

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
		return raw_data


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
		
