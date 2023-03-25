from modules.notion  import *

# Use Functions
final_df = get_all_notion_data(notion_key)
insert_data_into_table(final_df, "../health_data.db", "notion_data")
#notion_df = query_notion_table()