import requests, os, time, json, io, warnings
import argparse, sys
from datetime import datetime

from crawlers.crawler_proto import CrawlerProto, ProfileData

class YouTubeCrawler(CrawlerProto):

	def __init__(self, results_directory):
		results_directory = results_directory + '/youtube/'
		if not os.path.isdir(results_directory):
			os.mkdir(results_directory)
		self.results_directory = results_directory

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

			requests_result = requests.get(url, headers={'Connection':'close'}).json()
			time.sleep(0.01)
			return requests_result

		def getChannelID(channel_name):

			"""
			Arguments:
				channel_name: The name of the channel to be queried.
			Returns:
				result: The result of querying the API for channel IDs
					matching the name.
			"""

			url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q=' + channel_name + '?&type=channel&key=' + self.get_secret()
			url2 ='https://www.googleapis.com/youtube/v3/channels?key='+self.get_secret()+'&forUsername='+channel_name+'&part=id'
			val = getRequests(url)
			result = None
			if val['items']:
				result = val['items'][0]['id']['channelId']
			return result

		def getPlaylistID(channel_name):

			"""
			Arguments:
				channel_name: The name of the channel to be queried.
			Returns:
				result: The result of querying the API for playlist
					IDs matching the name.
			"""

			url = 'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername='+ channel_name +'&key=' + self.get_secret()
			val = getRequests(url)
			result = None
			if val['items']:
				result = val['items'][0]['contentDetails']['relatedPlaylists']['uploads']
			return result

		def getBasicInfo(channel_id):

			"""
			Arguments:
				channel_id: The ID of the channel to be queried.
			Returns:
				result: The result of querying the API for basic info
					about the channel.
			"""

			url ='https://www.googleapis.com/youtube/v3/channels?id=' + channel_id +'&key='+self.get_secret()+'&part=statistics'
			val = getRequests(url)
			return val ['items'][0]['statistics']

		def getVideoList(playlist_id):
		   
			"""
			Arguments:
				playlist_id: The ID of the playlist to be queried.
			Returns:
				videoList: The result of querying the API for the
					list of videos on the playlist.
			"""

			# 50 video limit - order according to date
			url = 'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId='+playlist_id+'&key='+self.get_secret() +'&order=date'
			val = getRequests(url)
			val = val['items']
			videoList = []
			videoCount = len(val)

			for n in range(videoCount):
				videoList.append(val[n]['contentDetails']['videoId'])

			return videoList

		def getVidStats(videoList):

			"""
			Arguments:
				videoList: A list of the videos to be queried.
			Returns:
				post_list: A list of dictionaries containing statistics for
					each of the listed videos.
			"""

			post_list = []

			for vidId in videoList:
				post_data = {}

				url = 'https://www.googleapis.com/youtube/v3/videos?part=statistics&id=' + vidId + '&key=' + self.get_secret()
				val = getRequests(url)
				post_data['id'] = val['items'][0]['id']
				val = val['items'][0]['statistics']

				post_data['views'] = 0
				post_data['likes'] = 0
				post_data['dislikes'] = 0
				post_data['comments'] = 0
				post_data['favorites'] = 0

				if 'viewCount' in val:
					post_data['views'] = int(val['viewCount'])
				if 'likeCount' in val:
					post_data['likes'] = int(val['likeCount'])
				if 'dislikeCount' in val:
					post_data['dislikes'] = int(val['dislikeCount'])
				if 'commentCount' in val:
					post_data['comments'] = int(val['commentCount'])
				if 'favoriteCount' in val:
					post_data['favorites'] = int(val['favoriteCount'])            

				post_list.append(post_data)

			return post_list

		#####

		target = query_data[1]
		since = query_data[2]
		until = query_data[3]

		channel_name = target
		channel_id = getChannelID(channel_name)
		playlist_id = getPlaylistID(channel_name)
		if channel_id is None or playlist_id is None:
			print(channel_name)
			return [query_data, 0, []]

		statistics = getBasicInfo(channel_id)

		viewCount = int(statistics['viewCount'])
		subscriberCount = int(statistics['subscriberCount'])
		videoCount = int(statistics['videoCount'])
		totalLikes = 0
		totalDislikes = 0
		totalComments = 0
		totalfavorites = 0

		videoList = getVideoList(playlist_id)

		post_list = getVidStats(videoList)

		return [query_data, subscriberCount, post_list]


	def format(self, raw_data):
		
		"""
		Arguments:
			raw_data: Raw data returned by the crawl of a profile.
		Returns:
			ProfileData tuple of the formatted profile data.
		"""

		target = raw_data[0]
		followerCount = raw_data[1]
		postList = raw_data[2]

		return ProfileData(Artist_Name=target[0], Artist_Login=target[1], File_create_datetime=str(datetime.now()), Follower_Count=followerCount, Posts=postList)

	def set_secret(self, app_secret):

		"""
		Arguments:
			app_secret: The application secret of the YouTube app that
				was registered for API access.
		"""

		self._app_secret = app_secret

	def get_secret(self):

		"""
		Returns:
			The application secret used to access API resources.
		"""

		return self._app_secret
