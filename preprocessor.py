from datetime import datetime
import pandas as pd
import re

def parse_date(date_string):
    try:
        parsed_date = datetime.strptime(date_string, '%d/%m/%y, %I:%M %p - ')
        return parsed_date
    except ValueError as e:
        return str(e)

def preprocess(data):
    pattern = "\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{1,2}\s[ap]m\s-\s"
    message = re.split(pattern, data)
    dates = re.findall(pattern, data)
    non_empty_date_indices = [i for i, date in enumerate(dates) if date]
    filtered_messages = [message[i] for i in non_empty_date_indices]
    filtered_dates = [dates[i] for i in non_empty_date_indices]
    df = pd.DataFrame({'user_msg': filtered_messages, 'msg_date': filtered_dates})
    df['msg_date'] = df['msg_date'].apply(lambda x: parse_date(x))
    df.rename(columns={'msg_date': 'date'}, inplace=True)
    users = []
    messages = []
    for message in df['user_msg']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_msg'], inplace=True)
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
