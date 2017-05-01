import requests
import getpass
import time

# get the username and password securely so it's not sitting in the code here:
user = raw_input('Enter your Zendesk username: ')
pwd = getpass.getpass('Enter your Zendesk password: ')
org = raw_input('Enter your organization: ')

def deleteTickets(user, pwd, tixToDelete):
	print "deleting {0} tickets".format(len(tixToDelete))

	url = 'https://{0}.zendesk.com/api/v2/suspended_tickets/destroy_many.json?ids='.format(org)

	# create the URL
	for ticketID in tixToDelete:
		url += str(ticketID)
		url += ","

	# delete the tickets
	response = requests.delete(url, auth=(user, pwd))

	# print the response for confirmation - should be "Response [204]"
	print response.json

def getSuspendedTickets(user, pwd):
	# initial URL to request first 100 tickets
	url = 'https://{0}.zendesk.com/api/v2/suspended_tickets.json"'.format(org)

	hundreds = 1
	while True:
		print "on round ", hundreds

		# collect suspended ticket IDs here
		suspendedTickets = []
		response = requests.get(url, auth=(user, pwd))
		data = response.json()
		ticketList = data['suspended_tickets']

		# collect the IDs for the <= 100 suspended tickets
		for ticket in ticketList:
			suspendedTickets.append(ticket['id'])

		# if there are no tickts, break
		if len(suspendedTickets) == 0:
			break

		# delete the collected tickets
		deleteTickets(user, pwd, suspendedTickets)

		print "Deleting {0} tickets".format(len(suspendedTickets))

		suspendedTickets = []

		# throttle every 200 tickets to stay within the rate limit
		if hundreds % 4 == 0:
			time.sleep(45)
		hundreds += 1

		# continue with the next 100 tickets
		# url = data['next_page']
		# print url

getSuspendedTickets(user, pwd)
