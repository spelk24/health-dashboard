from modules.notion import *
from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import warnings
from datetime import datetime, timedelta

# suppress the FutureWarning message
warnings.filterwarnings('ignore', 'In a future version,*', FutureWarning)
notion_key = os.environ['notion_api']

app = Flask(__name__)

# Define numerical columns to plot
numerical_cols = [
  'morning_energy', 'health_rating', 'work_rating', 'life_rating'
]

# Get Notion Data
# final_df = get_all_notion_data(notion_key)
# insert_data_into_table(final_df, "health_data.db", "notion_data")
notion_df = query_notion_table()

# Colors
gridline_color = '#f0f0f0'
grid_color = "#252525"
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']


@app.route('/')
def index():
  # Get the date 30 days ago
  today = datetime.now().date()
  date_30_days_ago = (today - timedelta(days=30)).strftime('%Y-%m-%d')

  # Filter the data to the last 30 days
  plot_data = notion_df[notion_df['date'] >= date_30_days_ago]

  # Create a list of plots, one for each numerical column
  plots = []
  for i, col in enumerate(numerical_cols):
    fig = px.line(plot_data, x='date', y=col)

    # Set the background color of the plot to white
    fig.update_layout(plot_bgcolor='white', height=250)

    # Set the line color to a different color for each plot
    fig.update_traces(line_color=colors[i])

    # Set the y-axis scale to 0-10
    fig.update_yaxes(range=[0, 10])

    # Remove axis titles and plot title
    fig.update_layout(title='',
                      xaxis_title='',
                      yaxis_title='',
                      margin=dict(l=0, r=0, t=0, b=0))

    # Add major gridlines and x and y lines
    fig.update_xaxes(showgrid=True,
                     gridwidth=1,
                     gridcolor=gridline_color,
                     showline=True,
                     linewidth=1,
                     linecolor=grid_color,
                     automargin=0)
    fig.update_yaxes(showgrid=True,
                     gridwidth=1,
                     gridcolor=gridline_color,
                     showline=True,
                     linewidth=1,
                     linecolor=grid_color,
                     automargin=0)

    plots.append(fig.to_html(full_html=False))

  # Pass plots to index.html template
  return render_template('index.html', plots=plots)


app.run(host='0.0.0.0', port=8080)
