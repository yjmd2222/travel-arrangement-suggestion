import pandas as pd

df = pd.read_csv('weather_DB.csv', encoding='utf-8-sig')

# Convert the 'Day' column to integers
df['Day'] = df['Day'].astype(int)

def filter_weather_data(start_date, end_date):

    start_date = int(start_date.split('-')[2])
    end_date = int(end_date.split('-')[2])

    if end_date < start_date:
        return "End date should be greater than or equal to the start date."

    # Filter the desired period from the DataFrame
    filtered_df = df[(df['Day'] >= start_date) & (df['Day'] <= end_date)]
    filtered_df = filtered_df.reset_index(drop=True)

    # Display the filtered weather data using tabulate
    return filtered_df.to_dict('index')
