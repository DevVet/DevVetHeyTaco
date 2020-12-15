import sqlite3
from datetime import datetime

def init_db_conn():
    conn = sqlite3.connect('heyTaco.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS transations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        recipient TEXT NOT NULL,
        created INTEGER NOT NULL
    )
    ''')
    conn.commit()
    c.close()
    return conn



def add_transaction(conn, sender, recipient):
    c = conn.cursor()

    statement = '''
        INSERT INTO transations (sender, recipient, created) VALUES
        (?,?, ?)
    '''

    c.execute(statement,(sender, recipient, datetime.timestamp(datetime.now())))
    conn.commit()
    c.close()

def get_this_months_scores(conn):
    c = conn.cursor()

    statement = '''
        SELECT recipient, COUNT(recipient) AS score FROM transations 
        GROUP BY recipient
        ORDER BY score ASC
    '''

    data = [record for record in c.execute(statement)]
    c.close()
    return data

def has_given_today(conn, sender):
    c = conn.cursor()

    statement = '''
        SELECT created FROM transations
        WHERE sender=?
        LIMIT 5
    '''
    data = [datetime.fromtimestamp(record[0]) for record in c.execute(statement, (sender,))]
    c.close()
    
    return sum([dt.date() == datetime.today().date() for dt in data])