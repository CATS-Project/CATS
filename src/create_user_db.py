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

        print 'Inserting test users'
        
        conn.execute("""
        insert into user (username, password)
        values ('adrien', 'test')
        """)
        
        conn.execute("""
        insert into user (username, password)
        values ('michael', 'test')
        """)
        
        conn.execute("""
        insert into user (username, password)
        values ('ciprian', 'test')
        """)
    else:
        print 'Database exists, assume schema does, too.'