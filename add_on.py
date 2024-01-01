from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
extractor = URLExtract()

def fetch_stats(user_selects,df):
    if user_selects != 'Overall':
        df = df[df['user'] == user_selects]

    num_msg = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))


    num_media = df[df['message'] == '<Media omitted\n'].shape[0]
    return num_msg,len(words),num_media,len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df

def create_wordcloud(user_selects,df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if user_selects != 'Overall':
        df = df[df['user'] == user_selects]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(user_selects,df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if user_selects != 'Overall':
        df = df[df['user'] == user_selects]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_add_on(user_selects,df):
    if user_selects != 'Overall':
        df = df[df['user'] == user_selects]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(user_selects, df):
    if user_selects != 'Overall':
        df = df[df['user'] == user_selects]

    # Assuming you have a 'date' column from which you can extract 'year' and 'month'
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(user_selects, df):
    if user_selects != 'Overall':
        df = df[df['user'] == user_selects]

    # Assuming you have a 'date' column from which you can extract 'only_date'
    df['only_date'] = df['date'].dt.date

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_activity_map(user_selects, df):
    if user_selects != 'Overall':
        df = df[df['user'] == user_selects]
    df['day_name'] = df['date'].dt.day_name()
    # Check if 'day_name' column is available in the DataFrame
    if 'day_name' in df.columns:
        return df['day_name'].value_counts()
    else:
        # Handle the case where 'day_name' is not available
        return pd.Series()



def month_activity_map(user_selects,df):

    if user_selects != 'Overall':
        df = df[df['user'] == user_selects]

    return df['month'].value_counts()

import numpy as np

def activity_heatmap(user_selects, df):
    if user_selects != 'Overall':
        df = df[df['user'] == user_selects]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap

    
    