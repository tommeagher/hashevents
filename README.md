hashevents
==========

A Python script to track popular URLs and active Twitter users at conferences.

This was originally developed in preparation for IRE's 2013 Computer-Assisted Reporting conference in Louisville, Kentucky.

The idea was that I wanted to grab all of the tweets using the hashtag #NICAR13 and then do some basic queries against the accumulated tweets.

Here's how I did it:
The script authenticates with Twitter's new API and queries it for all of the "recent" tweets (about a week back) that contain the desired hashtag. It then assigns those results to objects representing each tweet (or "status" update) using the python-twitter module. 

The scraped.py module loops through the list of result objects and parcels out each piece into a variable that it inserts into the MySQL database.

The query.py module separately queries the populated database for the most used URLs and the Twitter users with the most tweets using the hashtag. It puts the results of each of those queries into JSON arrays. 

There are two html files that fairly clunkily ingest the JSON feeds and displays them as searchable, paginated tables using a custom Javascript library created by a colleague. The clunkiness is entirely a result of my own inexperience with Javascript. His library is lovely, really. A third file, an index.html, iframes those two tables into a single page. The whole thing is styled with Bootstrap's CSS framework. You can see a live example at [www.tommeagher.com/nicar13/] (http://www.tommeagher.com/nicar13/)

##Configuration
I tried to build this to make it as reusable as possible. To that end, there are several local_settings variables that you can adjust that will handle most of the configuration for you.

Because of its use of the collections module, this script requires that you use Python 2.7. It also makes extensive use of the python-twitter (imported as "twitter") and MySQL-python (imported as "MySQLdb") modules. They have their own dependencies, but if you pip install each of them, it should take care of itself. Finally, the script uses BeautifulSoup to handle the extraction of the text of a web page's <title> tag.

One thing that (currently) needs some hand-holding is the insertion of the individual tweets into the database. If you look in the scraped.py file, you'll see a note where the table name needs to be manually configured there. I ran out of time to fix that and hope TODO it in the future.

If you're going to use the html pages I made, you'll also need the Bootstrap CSS framework and the custom Thunderdome javascript library, which is in pre-alpha construction and not really ready for reuse. I'd bet you could probably do the display a lot better. It wasn't the highest priority for me in developing this.

##Feedback
This was a fun little project to build, but obviously I concentrated on gathering the data and querying the database. I'd love some feedback on ways to improve that and any suggestions on making the front-end display better. Please file an issue in this repo or email me at hello (at) tommeagher (dot) com.
