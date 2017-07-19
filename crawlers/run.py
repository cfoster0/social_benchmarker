import argparse

from facebook_crawler import FacebookCrawler
from instagram_crawler import InstagramCrawler

def main():

	# Set crawler target and parameters.
	parser = argparse.ArgumentParser()

	parser.add_argument("inputs", help="Set the .csv file from which inputs should be read.")
	parser.add_argument("results", help="Set the directory where results should be stored.")

	parser.add_argument("-f", "--facebook", action='store_true', help="If yes, this crawl will collect Facebook data.")
	parser.add_argument("-i", "--instagram", action='store_true', help="If yes, this crawl will collect Instagram data.")

	args = parser.parse_args()

	crawlers = []

	if args.facebook is True:
		fbc = FacebookCrawler(args.results)
		fbc.set_token('157949204752963','2aa1ebdf5aa5cb1e190ffdc21b032c99')
		fbc.set_profiles(args.inputs)
		crawlers.append(fbc)

	if args.instagram is True:
		igc = InstagramCrawler(args.results)
		igc.set_profiles(args.inputs)
		crawlers.append(igc)

	for crawler in crawlers:
		for profile in crawler:
			try:
				raw = crawler.query(profile)
				crawler.save(raw)
			except ValueError as ve:
				print(ve)
				continue

if __name__ == '__main__':
	main()