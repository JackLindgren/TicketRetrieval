#!/usr/bin/python

import requests
import getpass

user = raw_input('Enter your Zendesk username: ')
pwd = getpass.getpass('Enter your Zendesk password: ')
org = raw_input('Enter your organization: ')

SuspendedTickets = []

def getSubjects():
	# get messages from the messages.txt file
	f = open("messages.txt", "r")
	messages = f.read()
	messages = messages.split("\n")
	return messages

def getTickets(SuspendedTickets, user, pwd):
	url = 'https://{0}.zendesk.com/api/v2/suspended_tickets.json'.format(org)

	subjects = getSubjects()

	# Zendesk returns 100 tickets and provides a next page URL if there are more
	# so we need to iterate through each page of results
	while url:
	# make the get request for the search
		response = requests.get(url, auth=(user, pwd))
	# parse the data (or whatever this does)
		data = response.json()
	# this will hold the search results hash
		ticket_list = data['suspended_tickets']
	# for each result ticket, get the ID and put it in our array
		for ticket in ticket_list:
			# hardcoding the subject here...
			if ticket['subject'] == "Delivery Status Notification (Failure)":
			#if ticket['subject'] in subjects:
				SuspendedTickets.append(ticket['id'])
	# change the URL to the next page's URL and repeat
	# if there is no next page, the loop will end
		url = data['next_page']
	return SuspendedTickets

def recoverTickets(listOfTix, user, pwd):
	print "We are recovering these tickets:", listOfTix
	# base URL:
	recURL = "https://{0}.zendesk.com/api/v2/suspended_tickets/recover_many.json?ids=".format(org)
	# add ticket IDs to the URL:
	for ticket in listOfTix:
		recURL += str(ticket)
		recURL += ","
	# get rid of the final comma; probably a better way to do this...
	recURL = recURL[0:-1]
	print "With this URL:", recURL
	response = requests.put(recURL, auth=(user, pwd))
	if response.status_code != 200:
		print response

getTickets(SuspendedTickets, user, pwd)
print "There are", len(SuspendedTickets), "tickets to recover"
print SuspendedTickets
print "The tickets are above. There are", len(SuspendedTickets), "of them"

while SuspendedTickets:
	count = 0
	toRecover = []
	while count < 100 and SuspendedTickets:
		toRecover.append(SuspendedTickets.pop())
		count += 1
	print "We are requesting the recovery of these tickets:", toRecover
	recoverTickets(toRecover, user, pwd)
	toRecover = []
