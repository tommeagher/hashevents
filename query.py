import MySQLdb, json, collections
from datetime import datetime
from local_settings import *
from settings import *

def queried():

    from settings import JSONID
    #connect to the MySQL db 
    db = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASS, db=MYSQL_DB)
 
    #create a cursor for the select
    cur = db.cursor()
    
#    TABLESTARTID=settings.TABLESTARTID
    
    if JSONID==None:
        JSONID=0
    else:
        JSONID=JSONID
    
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

    rows1 = cur.fetchall()

    # Convert query to row arrays
 
    rowarray_list = []
    for row in rows1:
        t = (row[0], row[1], row[2])
        rowarray_list.append(t) 
    j = json.dumps(rowarray_list)
    rowarrays_file = 'data/earlarrays.json'
    f = open(rowarrays_file,'w')
    print >> f, j

    cur.execute("""
            select count(user_id) as count, user_screen_name, user_name, user_location
            from nicar13
            where twitid > %s
            group by user_id
            order by 1 desc;

            """ % JSONID)

    rows2 = cur.fetchall()
    updated = datetime.now()
    min=str(updated.minute)
    if len(min)==1:
        min="0"+min
    else:
        min=min
    time=str(updated.hour)+":"+min
    day=str(updated.month)+"/"+str(updated.day)+"/"+str(updated.year)
    # Convert query to row arrays
 

    objects_list = []
    for row in rows2:
        d = collections.OrderedDict()
        d['updtime']=time
        d['updday']= day
        d['count'] = row[0]
        d['user_screen_name'] = "@"+row[1]
        d['user_name'] = row[2]
        d['user_location']=row[3]
        objects_list.append(d)
 
    j = json.dumps(objects_list)
    objects_file = 'data/tweeps_objects.json'
    f = open(objects_file,'w')
    print >> f, j


    db.close()
    return objects_file, rowarrays_file