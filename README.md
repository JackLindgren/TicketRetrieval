# TicketRetrieval
Retrieves tickets from Zendesk API

Well, Zendesk changed their API so the bounce messages are no longer available as tickets so the main portion here no longer works. A new file here will let you delete any suspended tickets, though.

# Delete tickets
deleteSuspended.py - enter your Zendesk credentials, and deletes any suspended tickets.

# Artifacts
Before the API changes, this worked as follows:
getBounces.py would grab the attachments for all "bounce" tickets, with certain subject line matches. Then combinedWargs.sh would organize and grep them for the addresses. 
