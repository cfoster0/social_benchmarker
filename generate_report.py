import os, argparse, json, csv

GENRES = ['URBAN', 'ADULT CONTEMP', 'ROCK', 'POP', 'ELECTRONIC']
SIZES = ['0-10K', '10K-100K', '100K-250K', '250K-500K', '500K-2M', '2M+']
LIMITS = [0, 10000, 100000, 250000, 500000, 2000000] # Minimum limit for each size bucket

platforms = ['facebook', 'instagram', 'youtube']

def main():

	"""
	Arguments:
		inputs: A .csv file with the structure '[Genres], [Artist Name], [Artist Username] ...'
		results: A .csv name for the results to be placed in.
	"""

	parser = argparse.ArgumentParser()

	parser.add_argument("platform", type=str, choices=platforms, help="Set the platform the data is sourced from.")
	parser.add_argument("inputs", help="Set the .csv file from which inputs should be read.")
	parser.add_argument("data", help="Set the directory profile data can be read from.")
	parser.add_argument("output", help="Set the .csv file where the benchmarks should be stored.")

	args = parser.parse_args()

	genres, names, usernames = read_profile_data(args.inputs, args.data, args.platform)

	all_genres, all_buckets, all_sizes, all_engagements, all_ratios, stats = calculate_stats(genres, names, usernames, args.data, args.platform)

	save_stats(args.output, all_genres, all_buckets, all_sizes, all_engagements, all_ratios, stats)

def read_profile_data(fname, dirname, platform):
	
	"""
	Arguments:
		fname: The name of a file with profile data, extracted as a JSON object through our youtube_crawler.py script.
		dirname: The name of the directory profile data can be read from.
		platform: The name of the platform the data comes from.
	Returns:
		genres: List of genre strings, one per artist
		names: List of artist name strings, one per artist
		usernames: List of artist username strings, one per artist
	"""

	with open(fname, 'r') as csvfile:
		genres = []
		names = []
		usernames = []

		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		
		for row in reader:
			if os.path.exists("{cwd}/{dir}/{plat}/{name}.json".format(cwd=os.getcwd(), dir=dirname, plat=platform, name=row[1])):
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
	Returns:
		engagements: The count of the total engagements a post achieved.
		ratio: The engagement ratio on the post, calculated according to the data available
			for that platform.
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
	Returns:
		size: The artist's follower count.
		engagement_average: The artist's average per-post engagement.
		ratio_average: The artist's average per-post engagement ratio.
	"""

	with open("{cwd}/{dir}/{plat}/{name}.json".format(cwd=os.getcwd(), dir=dirname, plat=platform, name=name)) as f:
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
	Returns:
		all_genres: A dictionary mapping genres to lists of the artists within the genre.
		all_buckets: A dictionary mapping audience sizes to lists of the artists within that bucket.
		all_sizes: A dictionary mapping names of artists to their raw follower count.
		all_engagements: A dictionary mapping artist names to their average per-post engagement.
		all_ratios: A dictionary mapping artist names to their average engagement ratio.
		stats: A dictionary mapping genres to sizes to the average engagement and ratio for that subcategory.
	"""

	all_genres = {}
	for genre in GENRES:
		all_genres[genre] = []
	all_buckets = {}
	for size in SIZES:
		all_buckets[size] = []
	all_sizes = {}
	all_engagements = {}
	all_ratios = {}

	for name, username, artist_genres in zip(names, usernames, genres):
		size, engagement, ratio = profile_stats(name, dirname, platform)

		if size is None or engagement is None or ratio is None:
			continue
		
		if size >= LIMITS[-1]:
			all_buckets[SIZES[-1]].append(name)
		else:
			for limit in LIMITS:
				if size < limit:
					all_buckets[SIZES[LIMITS.index(limit) - 1]].append(name)
					break

		for genre in artist_genres:
			all_genres[genre].append(name)

		all_sizes[name] = size
		all_engagements[name] = engagement
		all_ratios[name] = ratio

	stats = {}
	for genre in GENRES:
		stats[genre] = {}

	for genre in GENRES:
		for size in SIZES:
			bucket_artists = set(all_genres[genre]).intersection(all_buckets[size])
			bucket_size = sum([all_sizes[artist] for artist in bucket_artists])/float(len(bucket_artists))
			bucket_engagement = sum([all_engagements[artist] for artist in bucket_artists])/float(len(bucket_artists))
			bucket_ratio = sum([all_ratios[artist] for artist in bucket_artists])/float(len(bucket_artists))
			stats[genre][size] = (bucket_size, bucket_engagement, bucket_ratio)

	return all_genres, all_buckets, all_sizes, all_engagements, all_ratios, stats

def save_stats(fname, all_genres, all_buckets, all_sizes, all_engagements, all_ratios, stats):
	
	"""
	Arguments:
		fname: The .csv file to save the stats to.
		all_genres: A dictionary mapping genres to a list of names of artists within that genre
		all_buckets: A dictionary mapping audience size buckets to a list of names of artists with those audience sizes
		all_sizes: A dictionary mapping names of artists to their raw follower count.
		all_engagements: A dictionary mapping names of artists to their raw engagement number
		all_ratios: A dictionary mapping names of artists to their engagement ratio
		stats: A dictionary of dictionaries mapping genres to buckets to the (reach, engagement number, & ratio for that bucket)
	"""

	with open(fname, 'w') as logfile:
		wr = csv.writer(logfile)
		wr.writerow(['Genre', 'Size', 'Name', 'Audience Size', 'Average Engagements/Post', 'Average Engagement Ratio'])
		for genre in GENRES:
			for size in SIZES:
				bucket_artists = set(all_genres[genre]).intersection(all_buckets[size])
				for artist in bucket_artists:
					wr.writerow([genre, size, artist, all_sizes[artist], all_engagements[artist], all_ratios[artist]])

		wr.writerow([])
		for genre in GENRES:
			for size in SIZES:
				wr.writerow([genre, size, '', stats[genre][size][0], stats[genre][size][1], stats[genre][size][2]])

if __name__ == "__main__":
	main()
