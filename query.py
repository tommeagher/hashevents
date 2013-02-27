import MySQLdb, json, collections
from datetime import datetime
from local_settings import *
from settings import *

#the function to query the MySQL db and create the JSON arrays that will populate the front-end display table.
def queried():
    #grab the ID of the tweet that you want to be the first in the aggregated group by query.    
    from settings import JSONID
    #connect to the MySQL db 
    db = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASS, db=MYSQL_DB)
 
    #create a cursor to use for the SQL queries
    cur = db.cursor()
    
    #If JSONID is empty, then just query the whole db    
    if JSONID==None:
        JSONID=0
    else:
        JSONID=JSONID
    
    #A query to grab all of the 4 cols of URLs and Titles and then count them as if they were in one long row. But since I haven't seen a tweet with even two URLs yet, this might have been unnecessarily complicated.
    #this populates the top tweeted URLs table
    cur.execute("""
            select count(tweeturl) as count, tweeturl, tweeturltitle
              from (
              select ID, tweeturl1 as tweeturl, tweeturltitle1 as tweeturltitle from NICAR13 as n1 where twitid > %s 
              UNION  
              select ID, tweeturl2 as tweeturl, tweeturltitle2 as tweeturltitle from NICAR13 as n2 where twitid >%s
              UNION 
              select ID, tweeturl3 as tweeturl, tweeturltitle3 as tweeturltitle from NICAR13 as n3 where twitid >%s
              UNION
              select ID, tweeturl4 as tweeturl, tweeturltitle4 as tweeturltitle from NICAR13 as n4 where twitid >%s) as n5
              Group by tweeturl
              order by 1 desc;""" , (JSONID, JSONID, JSONID, JSONID))
    #You've got to fetch the results of the query.
    rows1 = cur.fetchall()

    # Convert query to row arrays, using Tony DeBarros' tutorial. 
    rowarray_list = []
    for row in rows1:
        #adding the html here so that the URLs are clickable and jump out of the iframe.
        #TODO is this where I'll decode? Test it.
        t = (row[0], '<a href="'+str(row[1])+'" target="_parent">'+str(row[1])+'</a>', row[2])
        rowarray_list.append(t) 
    j = json.dumps(rowarray_list)
    #use environment variable from local_settings.py to dictate where the JSON is deposited.
    rowarrays_file = '%s/earlarrays.json' % DATA_DIR
    f = open(rowarrays_file,'w')
    #assign this to a javascript variable to make it easier to pass into the JS in the html
    print >> f, "var earlarrays = "
    print >> f, j

    #this query will create the top tweeps table
    cur.execute("""
            select count(user_id) as count, user_screen_name, user_name, user_location
            from NICAR13
            where twitid > %s
            group by user_id
            order by 1 desc;

            """ % JSONID)

    rows2 = cur.fetchall()
    #the idea here was to pass the last updated time in via the json. Sure there's a more elegant way to do this.
    updated = datetime.now()
    min=str(updated.minute)
    if len(min)==1:
        min="0"+min
    else:
        min=min
    #adjusting this because the time stamp is in Central time apparently
    time=str(updated.hour+1)+":"+min
    day=str(updated.month)+"/"+str(updated.day)+"/"+str(updated.year)
    # Convert query to key:value row arrays
     objects_list = []
    for row in rows2:
        d = collections.OrderedDict()
        d['updtime']=time
        d['updday']= day
        d['count'] = row[0]
        #TODO thinking I should try decode here too
        d['user_screen_name'] = '<a href="http://www.twitter.com/'+row[1]+'" target="_parent">'+'@'+row[1]+'</a>'
        d['user_name'] = row[2]
        d['user_location']=row[3]
        objects_list.append(d)
 
    j = json.dumps(objects_list)
    objects_file = '%s/tweeps_objects.json' % DATA_DIR
    f = open(objects_file,'w')
    #assigning this to the javascript variable for later
    print >> f, "var tweeps = "
    print >> f, j

    db.close()
    return objects_file, rowarrays_file
