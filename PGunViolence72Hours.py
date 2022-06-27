import datetime
import os
import shutil
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tweepy
import undetected_chromedriver as uc
from geopy.geocoders import Nominatim
from matplotlib import projections
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# pip insfrom transformers import LayoutLMTokenizer
from selenium.webdriver.common.by import By

import config

geolocator = Nominatim(user_agent="mass_geocode")

auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
bearer_token = config.bearer_token
api = tweepy.API(auth)
client = tweepy.Client(bearer_token=config.bearer_token)


options = webdriver.ChromeOptions()


options.add_argument("--disable-extensions")

driver = uc.Chrome(options=options, use_subprocess=True)


driver.get("https://www.gunviolencearchive.org/last-72-hours")

driver.maximize_window()

time.sleep(10)


folder = driver.find_element(By.XPATH, '//a[@class="button"]')


folder.click()

time.sleep(10)


folder = driver.find_element(By.XPATH, "//a[text()='Download']")


time.sleep(10)
folder.click()


time.sleep(30)

driver.quit()


new_filename = "72hoursdownloaded.csv"
# new_filename = "shootings.csv"
filepath = "c:/Users/Joe Wilson/Downloads"
filename = max(
    [filepath + "/" + f for f in os.listdir(filepath)], key=os.path.getctime
)
shutil.move(os.path.join(
    "C:/Coding/gunviolencetweter/", filename), new_filename)


df = pd.read_csv(new_filename)

df["query"] = ""
df["query"] = df["City Or County"] + " " + df["State"]

df["lat"] = ""
df["long"] = ""
df["address"] = ""

length = len(df)

print("Geocoding...")
for i in df.index:
    try:
        location = geolocator.geocode(df["query"][i])
        df.loc[i, "lat"] = location.latitude
        df.loc[i, "long"] = location.longitude
        df.loc[i, "address"] = location.address
        print(f"{i} of {length}")
    except:
        df.loc[i, "lat"] = ""
        df.loc[i, "long"] = ""
        df.loc[i, "address"] = ""

print("Geocoding Complete..")

print(df.head())

df["victims"] = ""

print("Calculating Victims...")
victims = 0
for i in df.index:
    killed = df.loc[i, "# Killed"]
    injured = df.loc[i, "# Injured"]
    victims = killed + injured
    df.loc[i, "victims"] = victims
    print(f"{i} of {length}")
print("calculating Victims Complete...")

print("Summing Victims...")
sum = df["victims"].sum()
print(f"Sum of Victims: {sum}")
print("Summing Victims Complete...")

temp_file = "72final.csv"

df.to_csv(temp_file)

df = pd.read_csv(temp_file)


print("Creating Plot...")
fig = go.Figure(
    data=go.Scattergeo(
        lon=df["long"],
        lat=df["lat"],
        text=df["query"],
        mode="markers",
        marker_size=df["victims"] * 8,
        marker_color="darkred",
    )
)


fig.update_geos(
    visible=True,
    resolution=110,
    scope="usa",
    showcountries=True,
    countrycolor="Black",
    showsubunits=True,
    subunitcolor="Black",
    showocean=True,
    oceancolor="Blue",
    showlakes=True,
    lakecolor="Blue",
    showrivers=True,
    riverwidth=2,
    rivercolor="Blue",
    framecolor="Black",
    countrywidth=3,
    bgcolor="darkorange",
)

fig.update_layout(
    title=f"Gun Violence Last 72 Hours - {sum} Victims",
    title_x=0.5,
    title_xanchor="center",
    title_y=0.93,
    paper_bgcolor="darkorange",
    font=dict(color="Black", size=60, family="Bernard MT Condensed"),
)


fig.add_annotation(
    dict(
        font=dict(color="black", size=40, family="Arial"),
        x=0,
        y=-0,
        showarrow=False,
        text="Source: @politwit1984 and www.gunviolencearchive.org",
        textangle=0,
        xanchor="left",
        xref="paper",
        yref="paper",
    )
)

now = datetime.datetime.now()

fig.add_annotation(
    dict(
        font=dict(color="black", size=40, family="Arial"),
        x=0.95,
        y=-0,
        showarrow=False,
        text=now.strftime("%m-%d-%Y"),
        textangle=0,
        xanchor="right",
        xref="paper",
        yref="paper",
    )
)

fig.write_image("72hoursgunviolence.png", width=1500, height=1000)
print("Creating Plot Complete...")


tweet_filename = "72hoursgunviolence.png"

media = api.media_upload(tweet_filename)

tweet = "Gun Violence Last 72 Hours #VoteThemOut #EndGunViolence #moleg"
post_result = api.update_status(status=tweet, media_ids=[media.media_id])

time.sleep(2)

if os.path.exists(new_filename):
    os.remove(new_filename)

if os.path.exists(temp_file):
    os.remove(temp_file)

if os.path.exists(tweet_filename):
    os.remove(tweet_filename)
