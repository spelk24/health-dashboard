# create a connection to the database
conn = sqlite3.connect('health_data.db')

# create a cursor object to execute SQL commands
c = conn.cursor()

# create a table to match the Notion dataframe
c.execute('''
          CREATE TABLE IF NOT EXISTS notion_data
          (date TEXT PRIMARY KEY,
           no_drinks INTEGER,
           no_binge_drinking INTEGER,
           journal_entry INTEGER,
           read_15_min INTEGER,
           morning_energy INTEGER,
           health_rating INTEGER,
           work_rating INTEGER,
           life_rating INTEGER)
          ''')

# commit changes to the database
conn.commit()