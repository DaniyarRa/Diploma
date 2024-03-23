import pandas as pd
import math
def get_actual_crimininal_data(step):
    df = pd.read_excel('assets/crime_data.xlsx')
    step_len = len(str(step).split('.')[1])
    df['Latitude'] = df['Latitude'].apply(lambda x: round((math.floor(x * (1 / step)) * step) + float(step), step_len))
    df['Longitude'] = df['Longitude'].apply(lambda x: round(math.floor(x * (1 / step)) * step, step_len))

    common_y_values = df.groupby('Crime Title')['Hard Code'].agg(lambda x: x.mode().iloc[0])

    df['Hard Code'] = df.apply(lambda row: common_y_values[row['Crime Title']] if row['Hard Code'] == 0 else row['Hard Code'], axis=1)

    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')

    current_month = pd.Timestamp.now().month

    df['slope'] = (df['Date'].dt.year - pd.Timestamp.now().year) * 12 + df['Date'].dt.month - current_month + 100
    df['slope'] = df['slope'].apply(lambda x: 0 if x < 0 else x)
    df['score'] = df['Hard Code'] * df['slope']

    df = df[['Latitude', 'Longitude', 'score']].groupby(by=['Latitude', 'Longitude']).sum('score').reset_index()

    #ATTENTATION GIVE coef
    df['score'] = df['score'].apply(lambda x: math.sqrt(math.sqrt(x / 100)))

    min_score = df['score'].min()
    max_score = df['score'].max()
    df['score'] = (df['score'] - min_score) / (max_score - min_score)

    data = df.set_index(['Latitude', 'Longitude'])['score'].to_dict()
    print('data_in_scoring:', data)
    return data