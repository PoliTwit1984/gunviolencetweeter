import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from urllib.request import urlopen
import json
import plotly.express as px

df = pd.read_csv("2020election2.csv")


with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
    
rank_fig = px.choropleth(df, geojson=counties, locations='fips', color='per_point_diff',
        color_continuous_scale="bluered",
        range_color=(-1, 1),
        scope="usa")



rank_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

rank_fig.show()