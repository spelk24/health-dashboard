from modules.notion import *
from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
colors = ['#66c2a5', '#fc8d62', '#e78ac3', '#377eb8']


@app.route('/')
def index():
  # Get the date 30 days ago
  today = datetime.now().date()
  date_30_days_ago = (today - timedelta(days=31)).strftime('%Y-%m-%d')
  date_60_days_ago = (today - timedelta(days=61)).strftime('%Y-%m-%d')

  # Filter the data to the last 30 days
  plot_data = notion_df[notion_df['date'] >= date_30_days_ago].reset_index()
  compare_data = notion_df[
    (notion_df['date'] >= date_60_days_ago)
    & (notion_df['date'] < date_30_days_ago)].reset_index()
  compare_data.drop("date", axis=1, inplace=True)
  extracted_col = plot_data["date"]
  compare_data.insert(1, "date", extracted_col)
  # Create a list of plots, one for each numerical column
  plots = []
  for i, col in enumerate(numerical_cols):
    fig = go.Figure()
    fig.add_trace(
      go.Scatter(x=plot_data["date"],
                 y=plot_data[col],
                 mode='lines',
                 name="Last 30 Days",
                 showlegend=False,
                 hovertemplate='%{x}: %{y:.0f}',
                 line=dict(color=colors[i], width=3)))

    fig.add_trace(
      go.Scatter(x=compare_data["date"],
                 y=compare_data[col],
                 mode='lines',
                 name="Prior 30 Days",
                 hoverinfo="skip",
                 showlegend=False,
                 line=dict(color='lightgray', width=2)))

    # Set the background color of the plot to white
    fig.update_layout(plot_bgcolor='white', height=210)

    # Set the y-axis scale to 0-10
    fig.update_yaxes(range=[0, 10])

    # Remove axis titles and plot title
    fig.update_layout(title='',
                      xaxis_title='',
                      yaxis_title='',
                      margin=dict(l=0, r=0, t=0, b=0),
                      hoverlabel=dict(bgcolor="white",
                                      font_size=12,
                                      font_family="Arial",
                                      bordercolor=colors[i]))

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
    plots.append(fig.to_html(full_html=False, config={'displayModeBar':
                                                      False}))

  # Pass plots to index.html template
  return render_template('index.html', plots=plots)


app.run(host='0.0.0.0', port=8080)
