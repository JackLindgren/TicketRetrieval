import requests
import os
import time
import getpass

# get the username and password securely so it's not sitting in the code here:
user = raw_input('Enter your Zendesk username: ')
pwd = getpass.getpass('Enter your Zendesk password: ')

# this array will store the bounce ticket IDs
BounceTickets = []

def getTickets(message, BounceTickets, user, pwd):
	url = 'https://speedgauge.zendesk.com/api/v2/search.json?query=type:ticket status:new subject:"{0}" group:"Bounce emails"'.format(message)
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

messages = ["Delivery Status Notification", "Undeliverable: ", "Undelivered Mail Returned to Sender"]
for message in messages:
	BounceTickets = getTickets(message, BounceTickets, user, pwd)

print BounceTickets