import argparse

import pathos.multiprocessing as mp

from crawlers.facebook_crawler import FacebookCrawler
from crawlers.instagram_crawler import InstagramCrawler
from crawlers.youtube_crawler import YouTubeCrawler

facebook_app = None # Fill me in with your Facebook application ID string
facebook_secret = None # Fill me in with your Facebook application secret string
youtube_key = None # Fill me in with your YouTube application key string

platforms = ['facebook', 'instagram', 'youtube']

def main():

	# Set crawler target and parameters.
	parser = argparse.ArgumentParser()

	parser.add_argument("platform", type=str, choices=platforms, help="Set the platform the data is sourced from.")
	parser.add_argument("inputs", help="Set the .csv file from which inputs should be read.")
	parser.add_argument("results", help="Set the directory where results should be stored.")

	args = parser.parse_args()

	p = mp.Pool(4)

	if args.platform == 'facebook':
		if facebook_app is None or facebook_secret is None:
			raise ValueError("Facebook application ID and secret must be provided.")
		fbc = FacebookCrawler(args.results)
		fbc.set_token(facebook_app, facebook_secret)
		fbc.set_profiles(args.inputs)
		fbclist = list(fbc)
		rawqueries = p.map(fbc.query, fbclist)
		p.map(fbc.save, rawqueries)

	elif args.platform == 'instagram':
		igc = InstagramCrawler(args.results)
		igc.set_profiles(args.inputs)
		igclist = list(igc)
		rawqueries = p.map(igc.query, igclist)
		p.map(igc.save, rawqueries)

	elif args.platform == 'youtube':
		if youtube_key is None:
			raise ValueError("YouTube application key must be provided.")
		ytc = YouTubeCrawler(args.results)
		ytc.set_secret(youtube_key)
		ytc.set_profiles(args.inputs)
		ytclist = list(ytc)
		rawqueries = p.map(ytc.query, ytclist)
		p.map(ytc.save, rawqueries)

	else:
		raise NotImplementedError("Platform {plat} has not been implemented. The valid platforms are: {platlist}.".format(plat=args.platform, platlist=str(platforms)))

	p.close()


if __name__ == '__main__':
	main()