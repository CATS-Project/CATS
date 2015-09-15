__author__ = "Adrien Guille"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "adrien.guille@univ-lyon2.fr"
__status__ = "Production"

import os
import sqlite3

db_filename = 'users.db'
schema_filename = 'user_db.schema'

db_is_new = not os.path.exists(db_filename)

with sqlite3.connect(db_filename) as conn:
    if db_is_new:
        print 'Creating schema'
        with open(schema_filename, 'rt') as f:
            schema = f.read()
        conn.executescript(schema)

        print 'Inserting default data'
        
        conn.execute("""
        insert into user (username, password, can_collect_tweets)
        values ('demo', 'demo', 'False')
        """)
        
        conn.execute("""
        insert into user (username, password, can_collect_tweets)
        values ('michael', 'test', 'True')
        """)

        conn.execute("""
        insert into collection (username, start, duration, language, keyword, location, user, running)
        values ('demo', '2015-04-06', '60', 'English', 'None', '49.186288,0.043709,53.186288,-8.043709', 'None', 'False')
        """)
    else:
        print 'Database exists, assume schema does, too.'