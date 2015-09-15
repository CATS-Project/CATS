__author__ = "Adrien Guille"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "adrien.guille@univ-lyon2.fr"
__status__ = "Production"

import sys
import os
import sqlite3

db_filename = 'users.db'

if len(sys.argv) == 3:
    if not os.path.exists('streaming/data/'+sys.argv[0]):
        os.makedirs('streaming/data/'+sys.argv[0])
        os.makedirs('mabed/input/'+sys.argv[0])
        with sqlite3.connect(db_filename) as conn:
            conn.execute("insert into user (username, password, can_collect_tweets) values ('"+sys.argv[0]+
                         "', '"+sys.argv[1]+"', '"+sys.argv[2]+"')")
    else:
        print 'User', sys.argv[0], 'already exists!'
