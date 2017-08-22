import os, argparse, json, csv

GENRES = ['URBAN', 'ADULT CONTEMP', 'ROCK', 'POP', 'ELECTRONIC']
SIZES = ['0-10K', '10K-100K', '100K-250K', '250K-500K', '500K-2M', '2M+']
LIMITS = [0, 10000, 100000, 250000, 500000, 2000000] # Minimum limit for each size bucket

def main():

	"""
	Arguments:
		inputs: A .csv file with the structure '[Genres], [Artist Name], [Artist Username] ...'
		results: A .csv name for the results to be placed in.
	"""

	parser = argparse.ArgumentParser()

	parser.add_argument("inputs", help="Set the .csv file from which inputs should be read.")
	parser.add_argument("data", help="Set the directory profile data can be read from.")
	parser.add_argument("results", help="Set the .csv file where the results should be stored.")
	parser.add_argument("platform", type=str, choices=['facebook', 'instagram', 'youtube'])
	#SKETU(JGNEHRE)

	args = parser.parse_args()

	genres, names, usernames = read_profile_data(args.inputs, args.data, args.platform)

	all_genres, all_sizes, all_engagements, all_ratios, stats = calculate_stats(genres, names, usernames, args.data, args.platform)

	save_stats(args.results, all_genres, all_sizes, all_engagements, all_ratios, stats)

def read_profile_data(fname, dirname, platform):
	
	"""
	Arguments:
		fname: The name of a file with profile data, extracted as a JSON object through our youtube_crawler.py script.
		dirname: The name of the directory profile data can be read from.
		platform: The name of the platform the data comes from.
	"""

	with open(fname, 'r') as csvfile:
		genres = []
		names = []
		usernames = []

		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		
		for row in reader:
			if os.path.exists(os.getcwd() + '/' + dirname + '/' + platform + '/' + row[1] + '.json'):
				profile_genres = []
				for genre in row[0].split('/'):
					if genre in GENRES:
						profile_genres.append(genre)
				genres.append(profile_genres)
				names.append(row[1])
				usernames.append(row[2])

		return genres, names, usernames

def post_stats(post, size, platform):

	"""
	Arguments:
		post: A JSON object of the post to return engagement stats for.
		size: Size of the profile's following.
		platform: The name of the platform the data comes from.
	"""

	if platform == 'facebook':
		engagements = post['shares'] + post['comments']
		for reaction in post['reactions']:
			engagements += post['reactions'][reaction]
		ratio = engagements / float(size)
	elif platform == 'instagram':
		engagements = post['likes'] + post['comments']
		ratio = engagements / float(size)
	elif platform == 'youtube':
		engagements = post['likes'] + post['dislikes'] + post['dislikes'] + post['comments'] + post['favorites']
		if post['views'] is 0:
			ratio = None
		else:
			ratio = engagements / float(post['views'])
	else:
		raise NotImplementedError
	
	return engagements, ratio

def profile_stats(name, dirname, platform):

	"""
	Arguments:
		name: The name (as a string) of the artist whose stats should be returned.
		dirname: The name of the directory profile data can be read from.
		platform: The name of the platform the data comes from.
	"""

	with open(os.getcwd() + '/' + dirname + '/' + platform + '/' + name + '.json') as f:
		data = json.load(f)

	size = data['Follower_Count']

	posts = data['Posts']
	number_of_posts = len(posts)

	engagements_total = 0
	ratio_total = 0

	for post in posts:
		post_engagements, post_ratio = post_stats(post, size, platform)
		if post_ratio is None:
			number_of_posts -= 1
		else:
			engagements_total += post_engagements
			ratio_total += post_ratio

	if engagements_total is 0:
		engagement_average = None
	else:
		engagement_average = engagements_total/float(number_of_posts)
	
	if ratio_total is 0:
		ratio_average = None
	else:
		ratio_average = ratio_total/float(number_of_posts)

	return size, engagement_average, ratio_average

def calculate_stats(genres, names, usernames, dirname, platform):
	
	"""
	Arguments:
		genres: A list of genre strings, ordered as the profiles were read in
		names: A list of artist name strings, ordered as the profiles were read in
		usernames: A list of username (i.e. channel name) strings, ordered as the profiles were read in
		dirname: The name of the directory profile data can be read from.
		platform: The name of the platform the data comes from.
	"""

	all_genres = {}
	for genre in GENRES:
		all_genres[genre] = []
	all_sizes = {}
	for size in SIZES:
		all_sizes[size] = []
	all_engagements = {}
	all_ratios = {}

	for name, username, artist_genres in zip(names, usernames, genres):
		size, engagement, ratio = profile_stats(name, dirname, platform)

		if size is None or engagement is None or ratio is None:
			continue
		
		if size >= LIMITS[-1]:
			all_sizes[SIZES[-1]].append(name)
		else:
			for limit in LIMITS:
				if size < limit:
					all_sizes[SIZES[LIMITS.index(limit) - 1]].append(name)
					break

		for genre in artist_genres:
			all_genres[genre].append(name)

		all_engagements[name] = engagement
		all_ratios[name] = ratio

	stats = {}
	for genre in GENRES:
		stats[genre] = {}

	for genre in GENRES:
		for size in SIZES:
			bucket_artists = set(all_genres[genre]).intersection(all_sizes[size])
			bucket_engagement = sum([all_engagements[artist] for artist in bucket_artists])/float(len(bucket_artists))
			bucket_ratio = sum([all_ratios[artist] for artist in bucket_artists])/float(len(bucket_artists))
			stats[genre][size] = (bucket_engagement, bucket_ratio)

	return all_genres, all_sizes, all_engagements, all_ratios, stats

def save_stats(fname, all_genres, all_sizes, all_engagements, all_ratios, stats):
	
	"""
	Arguments:
		fname: The .csv file to save the stats to.
		all_genres: A dictionary mapping genres to a list of names of artists within that genre
		all_sizes: A dictionary mapping audience sizes to a list of names of artists with those audience sizes
		all_engagements: A dictionary mapping names of artists to their raw engagement number
		all_ratios: A dictionary mapping names of artists to their engagement ratio
		stats: A dictionary of dictionaries mapping genres to buckets to the (engagement number & ratio for that bucket)
	"""

	with open(fname, 'w') as logfile:
		wr = csv.writer(logfile)
		wr.writerow(['Genre', 'Size', 'Name', 'Average Engagements/Post', 'Average Engagement Ratio'])
		for genre in GENRES:
			for size in SIZES:
				bucket_artists = set(all_genres[genre]).intersection(all_sizes[size])
				for artist in bucket_artists:
					wr.writerow([genre, size, artist, all_engagements[artist], all_ratios[artist]])

		wr.writerow([])
		for genre in GENRES:
			for size in SIZES:
				wr.writerow([genre, size, '', stats[genre][size][0], stats[genre][size][1]])

if __name__ == "__main__":
	main()
