import MySQLdb
import os
from datetime import datetime
from local_settings import *

db = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASS, db=MYSQL_DB)
cursor = db.cursor()

cursor.execute("SHOW DATABASES")

results = cursor.fetchall()
print results
cursor.close()
db.close()

#ignores the "information schema" database
results = results[1:]

now=datetime.now()
mydate=str(now.year) + "_" + str(now.month) + "_" + str(now.day)

for result in results:
    backupfile=result[0]+mydate+".sql.gz"
    cmd="echo 'Back up "+result[0]+" database to backups/"+backupfile+"'"
    os.system(cmd)
    cmd="mysqldump -u "+MYSQL_USER+" -h "+MYSQL_HOST+" -p"+MYSQL_PASS+" --opt --routines --flush-privileges --single-transaction --database "+result[0]+" | gzip -9 --rsyncable > backups/"+backupfile
    os.system(cmd)
