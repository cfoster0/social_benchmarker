import argparse

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
    	from facebook_crawler import FacebookCrawler
		fbc = FacebookCrawler(args.results)
		fbc.setProfiles(args.inputs)
		crawlers.push(fbc)

	if args.instagram is True:
		from instagram_crawler import InstagramCrawler
		igc = InstagramCrawler(args.results)
		igc.setProfiles(args.inputs)
		crawlers.push(igc)

	for crawler in crawlers:
		for profile in crawler:
			crawler.save(crawler.query(profile))

if __name__ == '__main__':
	main()