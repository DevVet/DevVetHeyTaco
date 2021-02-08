from datetime import datetime
import psycopg2
from config import config

def init_db_conn():
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
        # display the PostgreSQL database server version
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)

        statement = '''
            CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            sender VARCHAR(50) NOT NULL,
            recipient VARCHAR(50) NOT NULL,
            created TIMESTAMP NOT NULL
            )
        '''
        cur.execute(statement)
       
	# close the communication with the PostgreSQL
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return conn
      


def add_transaction(conn, sender, recipient):
    c = conn.cursor()

    statement = '''
        INSERT INTO transactions (sender, recipient, created) VALUES
        (%s,%s,%s)
    '''

    c.execute(statement,(sender, recipient, datetime.utcnow()))
    conn.commit()
    c.close()

def get_this_months_scores(conn):
    c = conn.cursor()

    statement = '''
        SELECT recipient, COUNT(recipient) AS score FROM transactions 
        WHERE extract(month from created) = extract(month from now()) and extract(year from created) = extract(year from now())
        GROUP BY recipient
        ORDER BY score desc
    '''
    c.execute(statement)
    data = [record for record in c.fetchall()]
    c.close()
    return data

def has_given_today(conn, sender):
    c = conn.cursor()

    statement = '''
        SELECT created FROM transactions
        WHERE sender='%s'
        LIMIT 5
    '''
    c.execute(statement, (sender,))
    data = c.fetchall()
    c.close()
    
    return sum([dt[0].date() == datetime.today().date() for dt in data])