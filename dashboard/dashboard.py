import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt

# Load processed dataset
day_df = pd.read_csv('https://raw.githubusercontent.com/bagusakhlaq/DICODING-Bike_Sharing_Dashboard/main/dashboard/day_df.csv')
hour_df = pd.read_csv('https://raw.githubusercontent.com/bagusakhlaq/DICODING-Bike_Sharing_Dashboard/main/dashboard/hour_df.csv')

df_list = [day_df, hour_df]

# Set the date column data type into datetime 
for df in df_list:
    df['date'] = pd.to_datetime(df['date'])

# Set the categorical data based on their order
months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
day_order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

yearmonth_order = day_df.yearmonth.unique()
yearmonth_order = yearmonth_order.tolist()

for df in df_list:
    df['month_name'] = pd.Categorical(df['month_name'], categories=months_order, ordered=True)
    df['day_name'] = pd.Categorical(df['day_name'], categories=day_order, ordered=True)
    df['yearmonth'] = pd.Categorical(df['yearmonth'], categories=yearmonth_order, ordered=True)

# Create date filter
min_date = day_df['date'].min()
min_ym = day_df['yearmonth'].min()

max_date = day_df['date'].max()
max_ym = day_df['yearmonth'].max()

day_df = day_df[((day_df['date'] >= str(min_date)) & (day_df['date'] <= str(max_date))) |
                (day_df['yearmonth'] >= str(min_ym)) & (day_df['yearmonth'] <= str(max_ym))]
hour_df = hour_df[(hour_df['date'] >= str(min_date)) & (hour_df['date'] <= str(max_date))]

# ---------------------------- Dashboard Making ------------------------------------------

# Set the dashboard title
col1, col2 = st.columns(2)

with col1:
    st.image("https://github.com/bagusakhlaq/DICODING-Bike_Sharing_Dashboard/blob/main/assets/logo.png?raw=true")

with col2:
    st.header("Bike Share Dashboard")

# Create bike user trend
st.subheader("Bike User Trend")

tab1, tab2 = st.tabs(['Monthly', 'Season-wise'])

with tab1:
    # Plot the total user trend
    trend_data = day_df.groupby('yearmonth')[['casual', 'registered', 'total']].sum().reset_index()

    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(10,6))

    sns.lineplot(data=trend_data, x='yearmonth', y='casual', color='skyblue', errorbar=None, label='casual')
    sns.lineplot(data=trend_data, x='yearmonth', y='registered', color='lightcoral', errorbar=None, label='registered')
    sns.lineplot(data=trend_data, x='yearmonth', y='total', color='dodgerblue', errorbar=None, label='total')
    plt.title("Monhtly Total User Trend From 2011 to 2012")
    plt.ylabel(None)
    plt.xlabel(None)
    plt.xticks(rotation=45, fontsize=8)
    plt.legend(loc='upper left')

    st.pyplot(fig)

with tab2:
    # Create total user trend based on season
    yvalue = hour_df.groupby(['date', 'yearmonth', 'season'])['total'].sum().reset_index()
    yvalue = yvalue[yvalue['total'] != 0]

    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(10,4))

    sns.pointplot(data=yvalue, x='yearmonth', y='total', hue='season', palette='tab10')
    plt.title("Total Users Trend Based on Season in 2011-2012")
    plt.ylabel(None)
    plt.xlabel(None)
    plt.xticks(rotation=45, fontsize=8)

    st.pyplot(fig)


# Create total users in every season barplot
st.subheader("User Preferences")

tab1, tab2 = st.tabs(['Favourite Season', 'Favourite Weather'])

with tab1:
    color_list = ['#1565c0','#bbdefb', '#bbdefb', '#bbdefb']

    df = hour_df.groupby('season')['total'].sum().reset_index()
    df = df.sort_values('total', ascending=False)

    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(data=df, 
                x='total', y='season', 
                errorbar=None, 
                palette=color_list)
    plt.title("Most Favourite Season to Ride a Bike")
    plt.xlabel(None)
    plt.ylabel(None)

    st.pyplot(fig)

with tab2:
    # Create total users by weather barplot
    weather_plot = hour_df[['date', 'yearmonth', 'weather', 'total']]

    weather_plot.replace({'weather': ['Clear, Few clouds, Partly cloudy',
                                    'Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist',
                                    'Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds',
                                    'Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog']},
                        {'weather': ['Clear', 'Mist', 'Light Snow, Light Rain', 'Heavy Rain, Snow, Fog']},
                        inplace=True
                        )

    weather_plot = weather_plot.groupby('weather')['total'].sum().reset_index()
    weather_plot = weather_plot.sort_values('total', ascending=False)

    color_list = ['#1565c0', '#bbdefb', '#bbdefb', '#bbdefb']

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8,4))
    sns.barplot(data=weather_plot, x='total', y='weather', palette=color_list)
    plt.title("Total Bike Users in Different Weather Situation")
    plt.ylabel(None)
    plt.xlabel("Total User (in Million)")

    # Add data labels on the right side of the bars
    for p in ax.patches:
        width = p.get_width()
        plt.text(width, p.get_y() + p.get_height() / 2, f"{width:,.0f}", ha='left', va='center')

    st.pyplot(fig)


# Create daily users heatmap
st.subheader("Daily Bike Users")

tab1, tab2 = st.tabs(['2011', '2012'])

with tab1:
    toggle = st.toggle('Show data labels', key="1")
    if toggle:
        True
    else:
        False

    df = hour_df[hour_df['year'] == 2011]
    df = df.groupby(['month_name', 'day_name'])['total'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(6,8))
    sns.heatmap(data=df.pivot('month_name', 'day_name', 'total'), vmin=0, annot=toggle, fmt='d', cmap='rocket_r')
    ax.xaxis.tick_top()
    ax.set(xlabel='', ylabel='')
    plt.title("Daily Total Bike Users in 2011")

    st.pyplot(fig)

with tab2:
    toggle = st.toggle('Show data labels', key="2")
    if toggle:
        True
    else:
        False

    df = hour_df[hour_df['year'] == 2012]
    df = df.groupby(['month_name', 'day_name'])['total'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(6,8))
    sns.heatmap(data=df.pivot('month_name', 'day_name', 'total'), vmin=0, annot=toggle, fmt='d', cmap='rocket_r')
    ax.xaxis.tick_top()
    ax.set(xlabel='', ylabel='')
    plt.title("Daily Total Bike Users in 2012")

    st.pyplot(fig)

# Create User Time Activity
st.subheader("User Time Activity")

tab1, tab2 = st.tabs(['2011', '2012'])

with tab1:
    toggle = st.toggle('Show data labels', key="3")
    if toggle:
        True
    else:
        False

    df = hour_df[hour_df['year'] == 2011]
    df = df.groupby(['day_name', 'hour'])['total'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(6,8))
    sns.heatmap(data=df.pivot('hour', 'day_name', 'total'), vmin=0, annot=toggle, fmt='d', cmap='rocket_r')
    ax.xaxis.tick_top()
    ax.set(xlabel='', ylabel='')
    plt.title("In Depth of Daily Total Bike Users in 2011")

    st.pyplot(fig)

with tab2:
    toggle = st.toggle('Show data labels', key="4")
    if toggle:
        True
    else:
        False

    df = hour_df[hour_df['year'] == 2012]
    df = df.groupby(['day_name', 'hour'])['total'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(6,8))
    sns.heatmap(data=df.pivot('hour', 'day_name', 'total'), vmin=0, annot=toggle, fmt='d', cmap='rocket_r')
    ax.xaxis.tick_top()
    ax.set(xlabel='', ylabel='')
    plt.title("In Depth of Daily Total Bike Users in 2012")

    st.pyplot(fig)

