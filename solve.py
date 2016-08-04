import requests
import getpass

user = raw_input('Enter your Zendesk username: ')
pwd = getpass.getpass('Enter your Zendesk password: ')
org = raw_input('Enter your organization: ')

OpenBounceTickets = []

#url = 'https://{0}.zendesk.com/api/v2/search.json?query=type:ticket subject:"Delivery Status Notification (Failure)" group_id:21775730'.format(org)

def getTickets(SuspendedTickets, user, pwd):
	# hardcoding the subject again because this takes care of 90% of what I care about:
	url = 'https://{0}.zendesk.com/api/v2/search.json?query=type:ticket status:New subject:"Delivery Status Notification (Failure)" group_id:21775730'.format(org)
	while url:
		response = requests.get(url, auth=(user, pwd))
		data = response.json()
		ticket_list = data['results']
		for ticket in ticket_list:
			# double check - probably redundant
			if ticket['subject'] == "Delivery Status Notification (Failure)" and ticket['status'] != "Solved":
				OpenBounceTickets.append(ticket['id'])
		url = data['next_page']
	return OpenBounceTickets

def buildRequest(listOfTix):
	requestJSON = '{"tickets": ['
	# add IDs
	for ticket in listOfTix:
		requestJSON += '{"id": '
		requestJSON += str(ticket)
		requestJSON += ', "status": "solved"},'
	# remove last comma - probably a better way to do this:
	requestJSON = requestJSON[0:-1]
	requestJSON += ']}'
	return requestJSON

def solveTickets(listOfTix, user, pwd):
	solveURL = 'https://{0}.zendesk.com/api/v2/tickets/update_many.json'.format(org)
	solveREQ = buildRequest(listOfTix)
	# for ticket in listOfTix:
	# 	solveURL += str(ticket)
	# 	solveURL += ","
	# solveURL = solveURL[0:-1]
	headers = {'Content-Type': 'application/json'}
	response = requests.put(solveURL, solveREQ, headers=headers, auth=(user, pwd))
	if response.status_code != 200:
		# print response.json()
		print response.json()

getTickets(OpenBounceTickets, user, pwd)
print "There are", len(OpenBounceTickets), "tickets to solve"
raw_input('Continue?')

while OpenBounceTickets:
	count = 0
	toSolve = []
	while count < 100 and OpenBounceTickets:
		toSolve.append(OpenBounceTickets.pop())
		count += 1
	print "We are solving some tickets: ", toSolve
	solveTickets(toSolve, user, pwd)
	toSolve = []
