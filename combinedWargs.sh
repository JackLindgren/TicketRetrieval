#!/bin/bash

# :g = get the files with the Python downloaders
# :c = create the directory structure
# :s = sort the files into their folders
# :l = make the list of files
# :m = do the "message" bounces (the ones where it's in the ticket, not an attachmnent)

while getopts ":g :c :s :l" opt; do
	case $opt in
		g)
			echo "we'll get the files" >&2
			python getBounces.py
#1			python getMessages.py
			;;
		c)
			echo "we'll create the directory structure" >&2
			# create the directories
			mkdir "./Bounces$(date '+%Y-%m-%d')"
			# directories for the bounce responses
			mkdir "./Bounces$(date '+%Y-%m-%d')/BounceMessages"
			mkdir "./Bounces$(date '+%Y-%m-%d')/BounceMessages/SL/"
			mkdir "./Bounces$(date '+%Y-%m-%d')/BounceMessages/NonSL/"
#2			mkdir "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other"
			# directories for the original emails
			mkdir "./Bounces$(date '+%Y-%m-%d')/OriginalMessages"
			mkdir "./Bounces$(date '+%Y-%m-%d')/OriginalMessages/Alert/"
			mkdir "./Bounces$(date '+%Y-%m-%d')/OriginalMessages/Report/"
			echo "the directories have been created"
			;;
		s)
			echo "we'll sort the files"
			# move the bounce messages to the folder for the day's bounces
			mv ./unnamed_attachment_1* ./"Bounces$(date '+%Y-%m-%d')/BounceMessages/"
			# move the SL bounces to their folder
			grep -lsi 'suppression' ./"Bounces$(date '+%Y-%m-%d')/BounceMessages"/unnamed_attachment_1* | xargs -I '{}' mv '{}' ./"Bounces$(date '+%Y-%m-%d')/BounceMessages/SL"
			# move the rest of them to the non-SL bounce folder
			mv ./"Bounces$(date '+%Y-%m-%d')/BounceMessages"/unnamed_attachment_1* ./"Bounces$(date '+%Y-%m-%d')/BounceMessages/NonSL/"
#3			mv ./"failure notice"* "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other/"
#4			mv ./"Mail delivery failed"* "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other/"
			# move the original messages to their folder
			mv ./unnamed_attachment_2*eml* ./"Bounces$(date '+%Y-%m-%d')/OriginalMessages/"
			# move the report ones to their place
			grep -lsi '^subject.*report' ./"Bounces$(date '+%Y-%m-%d')/OriginalMessages"/unnamed_attachment_2* | xargs -I '{}' mv '{}' "./Bounces$(date '+%Y-%m-%d')/OriginalMessages/Report"
			# and the report ones to theirs
			grep -lsi '^subject.*alert' ./"Bounces$(date '+%Y-%m-%d')/OriginalMessages"/unnamed_attachment_2* | xargs -I '{}' mv '{}' "./Bounces$(date '+%Y-%m-%d')/OriginalMessages/Alert"
			;;
		l)
			echo "we'll make a list of the files"
			# go through the SL bounces and find the email addresses
			grep @ ./"Bounces$(date '+%Y-%m-%d')/BounceMessages/SL"/unnamed_attachment_1* | cut -f2 -d\; | cut -c2- | sort | uniq -c >  "Bounces$(date '+%Y-%m-%d')/SLadd$(date '+%Y-%m-%d').txt"
			# go through the non-SL bounces and find the email addresses
			grep @ ./"Bounces$(date '+%Y-%m-%d')/BounceMessages/NonSL"/unnamed_attachment_1* | cut -f2 -d\; | cut -c2- | sort | uniq -c >  ./"Bounces$(date '+%Y-%m-%d')/NonSLadd$(date '+%Y-%m-%d').txt"
#5			cat "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other/Mail delivery failed"* | grep @ | awk '!/amazonses/' | cut -f1 -d\: | sort | uniq -c >> ./"Bounces$(date '+%Y-%m-%d')/NonAttached$(date '+%Y-%m-%d').txt"
#6			head "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other/failure notice"* | grep @ | awk '!/amazonses/' | cut -f1 -d\: | sort | uniq -c >> ./"Bounces$(date '+%Y-%m-%d')/NonAttached$(date '+%Y-%m-%d').txt"
			grep 'To\:\ .*' ./"Bounces$(date '+%Y-%m-%d')/OriginalMessages/Report"/* | cut -f3 -d\: | cut -c2- | sort | uniq > "./Bounces$(date '+%Y-%m-%d')/ReportBounces.txt"
			grep 'To\:\ .*' ./"Bounces$(date '+%Y-%m-%d')/OriginalMessages/Alert"/* | cut -f3 -d\: | cut -c2- | sort | uniq > "./Bounces$(date '+%Y-%m-%d')/AlertBounces.txt"
			;;
		m)
			echo "getting and sorting the plaintext messages"
			python getMessages.py
			mkdir "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other"
			mv ./"failure notice"* "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other/"
			mv ./"Mail delivery failed"* "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other/"
			cat "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other/Mail delivery failed"* | grep @ | awk '!/amazonses/' | cut -f1 -d\: | sort | uniq -c >> ./"Bounces$(date '+%Y-%m-%d')/NonAttached$(date '+%Y-%m-%d').txt"
			head "./Bounces$(date '+%Y-%m-%d')/BounceMessages/Other/failure notice"* | grep @ | awk '!/amazonses/' | cut -f1 -d\: | sort | uniq -c >> ./"Bounces$(date '+%Y-%m-%d')/NonAttached$(date '+%Y-%m-%d').txt"
			;;
	esac
done
