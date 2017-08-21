import argparse, json, csv

def main():

	# Set crawler target and parameters.
	parser = argparse.ArgumentParser()

	parser.add_argument("inputs", help="Set the .csv file from which inputs should be read.")
	parser.add_argument("results", help="Set the .csv file where the results should be stored.")

	args = parser.parse_args()

	genres = []
	names = []
	usernames = []

	with open(args.inputs, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in reader:
			genres.append(row[0])
			names.append(row[1])
			usernames.append(row[2])

	sizes = []
	nposts = []
	engagements = []

	genrebuckets = ['URBAN', 'ADULT CONTEMP', 'ROCK', 'POP', 'ELECTRONIC']
	sizebuckets = ['0-10K', '10K-100K', '100K-250K', '250K-500K', '500K-2M', '2M+', 'None']
	lowerlimits = [0, 10000, 100000, 250000, 500000, 2000000]

	npostslists = {}
	engagementslists = {}

	avgnposts = {}
	avgengagements = {}

	for genre in genrebuckets:
		npostslists[genre] = {}
		engagementslists[genre] = {}

		avgnposts[genre] = {}
		avgengagements[genre] = {}
		for size in sizebuckets:
			npostslists[genre][size] = []
			engagementslists[genre][size] = []

	for name, genrelist in zip(names, genres):
		with open('results/instagram/' + name + '.json') as data_file:
			data = json.load(data_file)
			sizes.append(data['Follower_Count'])

			sizebucket = None
			if data['Follower_Count'] is None:
				sizebucket = sizebuckets[6]
			else:
				for ll in lowerlimits:
					if data['Follower_Count'] < ll:
						sizebucket = sizebuckets[lowerlimits.index(ll) - 1]
						break
				if sizebucket is None:
					sizebucket = sizebuckets[5]
			#print(data['Follower_Count'], sizebucket)

			for ll in lowerlimits:
				if data['Follower_Count'] is None: #
					sizebucket = sizebuckets[5] #
					break #
				if data['Follower_Count'] < ll:
					sizebucket = sizebuckets[lowerlimits.index(ll) - 1]
					#print(data['Follower_Count'], sizebucket)
					break

			nposts.append(len(data['Posts']))
			postengagements = []
			for post in data['Posts']:
				theirengagements = 0
				theirengagements += post['likes']
				theirengagements += post['comments']
				postengagements.append(theirengagements)
			if len(postengagements) > 0:
				engagementratio = sum(postengagements)/float(len(postengagements))
				engagements.append(engagementratio)
				for genre in genrelist.split('/'):
					if genre in genrebuckets:
						#print(name, genre, sizebucket)
						engagementslists[genre][sizebucket].append(engagementratio)
			else:
				engagements.append(None)

			for genre in genrelist.split('/'):
				if genre in genrebuckets:
					npostslists[genre][sizebucket].append(len(data['Posts']))
			#print(name, len(data['Posts']))
			#print(name, len(postengagements))

	#print(npostslists)
	#print(engagementslists)

	for genrebucket in genrebuckets:
		for sizebucket in sizebuckets:
			if float(len(npostslists[genrebucket][sizebucket])) > 0:
				avgnposts[genrebucket][sizebucket] = sum(npostslists[genrebucket][sizebucket])/float(len(npostslists[genrebucket][sizebucket]))
			else: 
				avgnposts[genrebucket][sizebucket] = 0

			if float(len(engagementslists[genrebucket][sizebucket])) > 0:
				avgengagements[genrebucket][sizebucket] = sum(engagementslists[genrebucket][sizebucket])/float(len(engagementslists[genrebucket][sizebucket]))
			else:
				avgengagements[genrebucket][sizebucket] = 0

			#print(len(npostslists[genrebucket][sizebucket]), len(engagementslists[genrebucket][sizebucket]))


	with open(args.results, 'wb') as logfile:
		wr = csv.writer(logfile)
		wr.writerow(['Genre', 'Name', 'Username', 'Follower Count', 'Number of Posts', 'Average Engagements/Post'])
		for genre, name, username, size, npost, engagement in zip(genres, names, usernames, sizes, nposts, engagements):
			wr.writerow([genre, name, username, size, npost, engagement])
		wr.writerow([])
		for genrebucket in genrebuckets:
			for sizebucket in sizebuckets:
				wr.writerow([genrebucket, '', '', sizebucket, avgnposts[genrebucket][sizebucket], avgengagements[genrebucket][sizebucket]])




if __name__ == '__main__':
	main()