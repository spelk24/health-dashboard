from notion_client import Client
import pandas as pd
import datetime
import sqlite3

def process_notion_db(results):
    # Define an empty list to store the data
    notion_df = pd.DataFrame(columns=[
        "date",
        "no_drinks",
        "no_binge_drinking",
        "journal_entry",
        "read_15_min",
        "morning_energy",
        "health_rating",
        "work_rating",
        "life_rating"
    ])
    for result in results["results"]:
        row = {
            "date": result["properties"]["Date"]["date"]["start"],
            "no_drinks": result["properties"]["No Drinks"]["checkbox"],
            "no_binge_drinking": result["properties"]["No Binge Drinking"]["checkbox"],
            "journal_entry": result["properties"]["Journal Entry"]["checkbox"],
            "read_15_min": result["properties"]["Read 15 Minutes"]["checkbox"],
            "morning_energy": result["properties"]["Morning Energy"]["number"],
            "health_rating": result["properties"]["Health"]["number"],
            "work_rating": result["properties"]["Work"]["number"],
            "life_rating": result["properties"]["Life"]["number"]
        }
        notion_df = notion_df.append(row, ignore_index=True)

    notion_df["date"] = pd.to_datetime(notion_df["date"])
    return notion_df

def get_all_notion_data():
    # API Key and DB ID
    notion = Client(auth="")
    database_id = "290db37697724cb79c3bd3a8cf6a7820"
    database = notion.databases.retrieve(database_id)

    # Store
    all_notion_df = []
    notion_data = []
    next_cursor = None

    # Loop
    while True:
        results = notion.databases.query(
            **{
                "database_id": database_id
            },
            start_cursor=next_cursor,
        )
        page_df = process_notion_db(results)
        all_notion_df.append(page_df)
        notion_data.extend(results)
        next_cursor = results.get("next_cursor")
        if not next_cursor:
            break

    final_df = pd.concat(all_notion_df, ignore_index=True)
    final_df["date"] = final_df['date'].dt.strftime('%Y-%m-%d')
    return final_df

def insert_data_into_table(df, db_path, table_name):
    # Create a connection object
    conn = sqlite3.connect(db_path)
    
    # Get a cursor object
    cur = conn.cursor()
    
    # Iterate over the rows of the DataFrame and insert them one by one
    for _, row in df.iterrows():
        values = tuple(row)
        placeholders = ",".join("?" * len(values))
        query = f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})"
        cur.execute(query, values)
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def query_notion_table(db="../health_data.db"):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    # Select all rows from the notion_daily table
    cursor.execute('SELECT * FROM notion_data')
    
    # Fetch all the results and store them in a DataFrame
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=['date', 'no_drinks', 'no_binge_drinking', 'journal_entry',
                                         'read_15_min', 'morning_energy', 'health_rating', 'work_rating', 'life_rating'])
    # Close the cursor and connection
    cursor.close()
    conn.close()    
    return df

# Use Functions
final_df = get_all_notion_data()
insert_data_into_table(final_df, "../health_data.db", "notion_data")
notion_df = query_notion_table()