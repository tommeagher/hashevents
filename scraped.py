import twitter, MySQLdb, urllib2, urllib, re, csv, sys
from BeautifulSoup import BeautifulSoup
from local_settings import *
from settings import *
from datetime import datetime
import csv, sys

#function to grab real urls and page titles from link shorteners or other URLs
def get_title(url):
    response=urllib.urlopen(url)
    realurl=response.geturl()
    #the rare error of someone tweeting a direct link to a jpg
    if realurl[-5:-1]==".jpe" or realurl[-4:-1]==".jp":
        title = "Probably a picture of a cat"            
    else:
#set the headers for the request if needed    
        header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': '*',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        #make another request with headers to the destination page of any link that had used a t.co or other shortener
        req=urllib2.Request(realurl, headers=header)
        response2 = urllib2.urlopen(req)
        #first try to soupify the response2 from request with the headers.
        try: 
            html=response2.read()
            soup=BeautifulSoup(html)
            title=soup.title.text.encode("utf-8")
        #if that fails, try the response without the headers, such as pictures tweeted within twitter. 
        except:
            html=response.read()
            soup=BeautifulSoup(html)
            title=soup.title.text.encode("utf-8")
    return realurl, title
    
#function to connect to the MySQL database, grab the newest tweet in it, then query the Twitter API for everything after that. Then it cycles through those tweets and dumps them into the db for later.
def scraped():    
    filename = ('errors.csv')

    #import the twitter module and instantiate the twitter api keys 
    api = twitter.Api(consumer_key=MY_CONSUMER_KEY,
                          consumer_secret=MY_CONSUMER_SECRET,
                          access_token_key=MY_ACCESS_TOKEN_KEY,
                          access_token_secret=MY_ACCESS_TOKEN_SECRET)
                      
    #If you need to test the connection, this will confirm the authentication with the api
    #print api.VerifyCredentials()

    #connect to the MySQL db, using the environment variables from local_settings.py
    db = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASS, db=MYSQL_DB)
 
    #create a cursor that you can use for SQL queries
    cur = db.cursor()

    #Create the table name based on the hashtag in local_settings.py
    if HASHTAG[0]=="#":
        tablename=HASHTAG[1:]
    else: 
        tablename=HASHTAG

    #Does the table already exist? If not, create it.
    try:
        cur.execute('select * from %s.%s;' % (MYSQL_DB, tablename))
    except:
        cur.execute('create table %s (id integer primary key auto_increment, created_at text not null, twitid bigint not null, source text null, twittext text not null, tweeturl1 text null, tweeturltitle1 text null, tweeturl2 text null, tweeturltitle2 text null, tweeturl3 text null, tweeturltitle3 text null, tweeturl4 text null, tweeturltitle4 text null, user_id bigint not null, user_screen_name text not null, user_name text not null, user_location text null, user_url text null, user_description text null, retweeted text null, retweet_count text null);' % tablename)
    db.commit()

    #query the database. If it's empty, use "None" for since_id, thus grabbing everything in the Twitter API with that hashtag, back about a week.    
    #if the db has records in it, grab the last one and its id and use that for sinceid
    cur.execute('select max(twitid) from %s.%s;' % (MYSQL_DB, tablename))
    sinceid=cur.fetchone()
    if sinceid[0]==None:
        sinceid=None
    else:
        sinceid=sinceid[0]

    pagenum=1 
 
    #In order to grab all the tweets in chronological order, you have to use "recent" so it's not mixing in "popular tweets"
    results = api.GetSearch(term=HASHTAG, per_page=100, since_id=sinceid, page=pagenum, result_type="recent")
    length = len(results)


    #start at pagenum=1, if the len of results is 100, then try it with pagenum=2, and so on.
    while length>99:
        pagenum=pagenum+1
        newres=api.GetSearch(term=HASHTAG, per_page=100, since_id=sinceid, page=pagenum, result_type="recent")
        results=results+newres
        length=len(newres)

    #sort the results from lowest (oldest id) to highest
    results=sorted(results, key=lambda result: result.id)   

    #loop through each result Status object and grab these items, assign them to variables.
    for result in results:
        created_at=str(result.created_at)
        twitid=str(result.id)
        source=result.source.encode("utf8")
        twittext=result.text.encode("utf8")
        user_screen_name=str(result.user.screen_name).encode("utf8")
        result_user=api.GetUser(user_screen_name)
        user_id=str(result_user.id)
        user_name=result_user.name.encode("utf8")
        user_location=result_user.location.encode("utf8")
        user_url=str(result_user.url)
        user_description=result_user.description.encode("utf8")
        retweeted=str(result.retweeted)
        retweet_count=str(result.retweet_count)
        #take the text and use the re (regex) module to search out any URLs that might be hiding in there.
        earls = re.findall(r'(https?://\S+)', twittext)
        earls_len=len(earls)
        if earls_len>0:
            try:
                if earls_len==1:
                    tweeturl1, tweeturltitle1 = get_title(earls[0])
                    tweeturl2, tweeturltitle2 = None, None
                    tweeturl3, tweeturltitle3 = None, None
                    tweeturl4, tweeturltitle4 = None, None
                elif earls_len==2:
                    tweeturl1, tweeturltitle1 = get_title(earls[0])
                    tweeturl2, tweeturltitle2 = get_title(earls[1])
                    tweeturl3, tweeturltitle3 = None, None
                    tweeturl4, tweeturltitle4 = None, None
                elif earls_len==3:
                    tweeturl1, tweeturltitle1 = get_title(earls[0])
                    tweeturl2, tweeturltitle2 = get_title(earls[1])
                    tweeturl3, tweeturltitle3 = get_title(earls[2])
                    tweeturl4, tweeturltitle4 = None, None
                else:
                    tweeturl1, tweeturltitle1 = get_title(earls[0])
                    tweeturl2, tweeturltitle2 = get_title(earls[1])
                    tweeturl3, tweeturltitle3 = get_title(earls[2])
                    tweeturl4, tweeturltitle4 = get_title(earls[3])
            except:
            #catching the errors in a csv file so I can go back and examine why it's throwing errors later
            #don't just fail silently, keep a log of failed tweets and then we can go back and figure why
                errors=[]

                now=datetime.now()
                mistake=sys.exc_info()                
                row = [ now, twittext, twitid, mistake ]
                errors.append(row)                
                with open(filename, 'a') as errorfile:
                    wtr = csv.writer(errorfile, delimiter='|')
                    wtr.writerows(errors)
        else: 
            tweeturl1, tweeturltitle1 = None, None
            tweeturl2, tweeturltitle2 = None, None
            tweeturl3, tweeturltitle3 = None, None
            tweeturl4, tweeturltitle4 = None, None
        #assign all of the variables to a tuple
#        print twittext                
        treble = (created_at, twitid, source, twittext, tweeturl1, tweeturltitle1, tweeturl2, tweeturltitle2, tweeturl3, tweeturltitle3, tweeturl4, tweeturltitle4, user_id, user_screen_name, user_name, user_location, user_url, user_description, retweeted, retweet_count)
        #print treble
        #Can't get the tablename variable to work in the insert statement, because of the extra single quotes for a string, so had to hard code it.
        #If you change this for other event hashtags, be sure to change the tablename here.
        cur.execute("""INSERT INTO `NICAR13` (created_at, twitid, source, twittext, tweeturl1, tweeturltitle1, tweeturl2, tweeturltitle2, tweeturl3, tweeturltitle3, tweeturl4, tweeturltitle4, user_id, user_screen_name, user_name, user_location, user_url, user_description, retweeted, retweet_count) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)""" , treble)
        db.commit()
        
    


    return "Done"
