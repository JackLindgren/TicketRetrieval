#!/usr/bin/python

# modification to gather crumbs WITH TICKET IDs
# this uses a dictionary so that when writing the attachment failes
# we can display the ticket ID that failed and see if there is a problem

import requests
import os
import time
import getpass
import operator

# get the username and password securely so it's not sitting in the code here:
user = raw_input('Enter your Zendesk username: ')
pwd = getpass.getpass('Enter your Zendesk password: ')
org = raw_input('Enter your organization: ')

# this array will store the bounce ticket IDs
BounceTickets = []

def getTickets(message, BounceTickets, user, pwd):
	url = 'https://{0}.zendesk.com/api/v2/search.json?query=type:ticket status:new subject:"{1}" group:"Bounce emails"'.format(org, message)
	# Zendesk returns 100 tickets and provides a next page URL if there are more
	# so we need to loop through each page of results
	while url:
	# make the get request for the search
		response = requests.get(url, auth=(user, pwd))
	# parse the data (or whatever this does)
		data = response.json()
	# this will hold the search results hash
		ticket_list = data['results']
	# for each result ticket, get the ID and put it in our array
		for ticket in ticket_list:
			BounceTickets.append(ticket['id'])
	# change the URL to the next page's URL and repeat
	# if there is no next page, the loop will end
		url = data['next_page']
	return BounceTickets

# there are three subject lines that we're looking for right now.
# if more come up, they can be added to the messages array:
messages = ["Delivery Status Notification ", "Undeliverable: ", "Undelivered Mail Returned to Sender", "Undeliverable mail ", "Delivery failure"]
for message in messages:
	BounceTickets = getTickets(message, BounceTickets, user, pwd)

noAttachments = []
noAttachments = getTickets("Mail delivery failed", noAttachments, user, pwd)

# tell us how many bounces we have
print "There are {0} bounce tickets".format(len(BounceTickets) + len(noAttachments))
# show me all the ticket IDs
BounceTickets = sorted(BounceTickets)
noAttachments = sorted(noAttachments)
print BounceTickets
print noAttachments

proceed = raw_input("Is that the correct number of tickets?\nShall we proceed? (y/n)")
if proceed == "n":
	exit()

# now we have an array, BouceTickets, with the IDs for all of our bounces
# we also have an array noAttachments for the tickets that have a message, not txt and eml files
# we will use those IDs to retrieve the URLs for the ticket attachments

# this will hold our URLs
#BounceAttachmentURLs = []
# it's gonna be a dictionary with {URL:ticketID}
BounceAttachmentURLs = {}

# how many tickets do we have, how many attachments, and how many requests to the ZD API have we made
numTix = 0
numAts = 0
numReqs = 0

# for each ticket ID
for ticket_id in BounceTickets:
	#retrieve the comments
	url = 'https://{0}.zendesk.com/api/v2/tickets/{1}/comments.json'.format(org, ticket_id)
	response = requests.get(url, auth=(user, pwd))

	# so that we don't exceed the 200 requests/minute limit, we will rest for 1 second every 3 requests 
	# 	if there are more than 200 tickets (201 requests / 3 = 67 seconds)
	numReqs += 1
	if numReqs % 3 == 0 and len(BounceTickets) > 150:
		time.sleep(1)

	# let us know if there was an HTTP error
	if response.status_code != 200:
		print response.status_code

	# get the comments
	data = response.json()
	my_comments = data['comments']
	# get the attachments for each comment (the IDs actually)
	for comment in my_comments:
		my_attachments = comment['attachments']
	# each comment can have more than one attachment, so
	# for each attachment:
	for attachment in my_attachments:
		# get all of the attachments
		this_attachment = my_attachments[my_attachments.index(attachment)]
		# and add them to the BounceAttachmentURLs array
		#BounceAttachmentURLs.append(this_attachment['content_url'])
		BounceAttachmentURLs[this_attachment['content_url']] = ticket_id
		numAts += 1
	# print "comment and attachments retrieved for ticket #{0}".format(numTix)
	print "comment and attachments retrieved for ticket #{0}".format(ticket_id)
	numTix += 1

# get the comments for the bounces where there is no attachment
noAttachmentComments = []
for ticket_id in noAttachments:
	url = 'https://{0}.zendesk.com/api/v2/tickets/{1}/comments.json'.format(org, ticket_id)
	response = requests.get(url, auth=(user, pwd))
	if response.status_code != 200:
		print response.status_code
	data = response.json()
	my_comments = data['comments']
	for comment in my_comments:
		noAttachmentComments.append(comment['body'])

# write those comments to their own file
try:
	with open("unattachedBounces.txt", 'w') as f:
		for comment in noAttachmentComments:
			f.write(comment)
	print "Unattached comments saved"
except UnicodeEncodeError:
	print "Could not write an attachment for ticket #{0}".format(AttachmentURL[1])
	pass

# show us all of our URLs
#for AttachmentURL in BounceAttachmentURLs:
#	print AttachmentURL

print "{0} attachment(s) for {1} ticket(s) have been retrieved.".format(numAts, numTix)

# so that we can run this downloader multiple times in the same folder:
myFiles = os.listdir('.')
myDownloads = []
myNumbers = []
for item in myFiles:
	if "unnamed_attachment" in item:
		myDownloads.append(item)

for dl in myDownloads:
	myNumbers.append(int(dl.split('(')[1].split(')')[0]))
# actual number of files downloaded
k = 1
# ID number to write to the file (based on the highest ID in the current directory)
if myNumbers:
	i = sorted(myNumbers)[-1] + 1
else:
	i = 1

#for AttachmentURL in BounceAttachmentURLs.keys():

# sorts according to the VALUES (i.e. the ticket numbers)
sortedAttachmentURLs = sorted(BounceAttachmentURLs.items(), key=operator.itemgetter(1))

# now access each attachment URL online and save it
for AttachmentURL in sortedAttachmentURLs:

	# get the part of the URL with the filename (because we have both .eml and other attachments)
	myFilename = AttachmentURL[0].split("name=")[1]

	# our saved file will use that name, and a digit so that they don't overwrite each other
	# we also want the file extension at the end so that we can open it more easily 
	myFilenameParts = myFilename.split('.')
	if ".eml" in myFilename:
		myFilename = myFilenameParts[0] + "({0})".format(i) + ".eml"
	else:
		myFilename = myFilenameParts[0] + "({0})".format(i)

	# get our attachment content
	r = requests.get(AttachmentURL[0])
	# not too fast:
	if len(sortedAttachmentURLs) > 175 and i % 3 ==0:
		time.sleep(1)
	# save it with our filename
	try:
		with open(myFilename, 'w') as f:
			f.write(r.text)
			print "{0} files saved (ticket {1})".format(k, AttachmentURL[1])
		i += 1
		k += 1
	except UnicodeEncodeError:
		print "Could not write an attachment for ticket #{0}".format(AttachmentURL[1])
		pass

print "The attachments have all been retrieved"

# tell me how much time I saved:
secondsSaved = len(BounceTickets) * 15
if secondsSaved < 60:
	minutes = 0
	seconds = secondsSaved
else:
	minutes = secondsSaved / 60
	seconds = secondsSaved - (60 * (minutes))

print "You just saved {0} minutes and {0} seconds".format(minutes, seconds)



