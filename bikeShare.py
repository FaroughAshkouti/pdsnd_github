import time
import pandas as pd
import numpy as np

CITY_DATA = {'chicago': 'chicago.csv',
             'new york city': 'new_york_city.csv',
             'washington': 'washington.csv'}

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june']
WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////
def get_filters():
    print('\n  This is US bikeshare data!\n')

    # get user input for city (chicago, new york city, washington).
    cities_list = []
    num_cities = 0
    for a_city in CITY_DATA:
        cities_list.append(a_city)
        num_cities += 1
        print('{0:20}. {1}'.format(num_cities, a_city.title()))

    while True:
        try:
            city_num = int(input("\nEnter a number for the city (1 - {}):  ".format(len(cities_list))))
        except:
            continue
        if city_num in range(1, len(cities_list) + 1):
            break
    city = cities_list[city_num - 1]

    # get user input for month (all, january, february, ... , june)
    while True:
        try:
            month = input("Enter the month with January=1, June=6 or 'a' for all:  ")
        except:
            print("Valid input:  1 - 6, a")
            continue

        if month == 'a':
            month = 'all'
            break
        elif month in {'1', '2', '3', '4', '5', '6'}:
            month = MONTHS[int(month) - 1]
            break
        else:
            continue

# get user input for day of week (all, monday, tuesday, ... sunday)
    while True:
        try:
            day = input("Enter the day with Monday=1, Sunday=7 or 'a' for all:  ")
        except:
            print("---->>  Valid input:  1 - 7, a")
            continue

        if day == 'a':
            day = 'all'
            break
        elif day in {'1', '2', '3', '4', '5', '6', '7'}:
            # reassign the string name for the day
            day = WEEKDAYS[int(day) - 1]  # here we MUST -1 to get correct index
            break
        else:
            continue
    return city, month, day


# /////////////////////////////////////////////////////////////////////////////////////////////////////////
def load_data(city, month, day):
    # load data file into a dataframe
    df = pd.read_csv(CITY_DATA[city])

    # convert the Start Time column to datetime
    df['Start Time'] = pd.to_datetime(df['Start Time'], errors='coerce')

    # extract month, day of week and hour from Start Time to create new columns
    df['month'] = df['Start Time'].dt.month  # range (1-12)
    df['day_of_week'] = df['Start Time'].dt.dayofweek  # range (0-6)
    df['hour'] = df['Start Time'].dt.hour  # range (0-23)

    init_total_rides = len(df)
    filtered_rides = init_total_rides  # initially

    # filter by month if applicable
    if month != 'all':
        # use the index of the MONTHS list to get the corresponding int
        month_i = MONTHS.index(month) + 1  # index() returns 0-based, so +1

        # filter by month to create the new dataframe
        df = df[df.month == month_i]
        month = month.title()

    # filter by day of week if applicable
    if day != 'all':
        # use the index of the WEEKDAYS list to get the corresponding int
        day_i = WEEKDAYS.index(day)  # index() returns 0-based, matches df

        # filter by day of week to create the new dataframe
        df = df[df.day_of_week == day_i]
        day = day.title()
    print('*************************************************************')
    return df


# /////////////////////////////////////////////////////////////////////////////////////////////////
# Converts an int hour time to string format with PM or AM.
def hour_12_str(hour):
    if hour == 0:
        str_hour = '12 AM'
    elif hour == 12:
        str_hour = '12 PM'
    else:
        str_hour = '{} AM'.format(hour) if hour < 12 else '{} PM'.format(hour - 12)

    return str_hour


# //////////////////////////////////////////////////////////////////////////////////////////////////

def time_stats(df):
    print('\nMost Frequent Times of Travel...')

    # display the most common month; convert to string
    month = MONTHS[df['month'].mode()[0] - 1].title()
    print('Month:               ', month)

    # display the most common day of week
    common_day = df['day_of_week'].mode()[0]  # day in df is 0-based
    common_day = WEEKDAYS[common_day].title()
    print('Day of the week:     ', common_day)

    # display the most common start hour; convert to 12-hour string
    hour = hour_12_str(df['hour'].mode()[0])
    print('Start hour:          ', hour)
    print('*************************************************************')


# /////////////////////////////////////////////////////////////////////////////////////////////////

def station_stats(df):
    print('  Most Popular Stations and Trip...')
    filtered_rides = len(df)

    # display most commonly used start station
    start_station = df['Start Station'].mode()[0]
    start_station_trips = df['Start Station'].value_counts()[start_station]

    print('\nStart station:       ', start_station)
    print('{0:30}{1}/{2} trips'.format(' ', start_station_trips, filtered_rides))

    # display most commonly used end station
    end_station = df['End Station'].mode()[0]
    end_station_trips = df['End Station'].value_counts()[end_station]

    print('End station:         ', end_station)
    print('{0:30}{1}/{2} trips'.format(' ', end_station_trips, filtered_rides))

    # display most frequent combination of start station and end station trip
    # group the results by start station and end station
    df_start_end_combination_gd = df.groupby(['Start Station', 'End Station'])
    most_freq_trip_count = df_start_end_combination_gd['Trip Duration'].count().max()
    most_freq_trip = df_start_end_combination_gd['Trip Duration'].count().idxmax()

    print('    Frequent trip:        {}, {}'.format(most_freq_trip[0], most_freq_trip[1]))
    print('{0:30}{1} trips'.format(' ', most_freq_trip_count))
    print('*************************************************************')


# /////////////////////////////////////////////////////////////////////////////////////////////

def seconds_to_HMS_str(total_seconds):
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    day_hour_str = ''
    if weeks > 0:
        day_hour_str += '{} weeks, '.format(weeks)
    if days > 0:
        day_hour_str += '{} days, '.format(days)
    if hours > 0:
        day_hour_str += '{} hours, '.format(hours)
    if minutes > 0:
        day_hour_str += '{} minutes, '.format(minutes)

    # always show the seconds, even 0 secs when total > 1 minute
    if total_seconds > 59:
        day_hour_str += '{} seconds'.format(seconds)

    return day_hour_str


# /////////////////////////////////////////////////////////////////////////////////////////////////

def trip_duration_stats(df):
    print('\nTrip Duration...')

    # display total travel time; cast to int, we don't need fractions of seconds!
    total_travel_time = int(df['Trip Duration'].sum())
    print('Total travel time:   ', total_travel_time, 'seconds')
    print('   ', seconds_to_HMS_str(total_travel_time))

    # display mean travel time
    mean_travel_time = int(df['Trip Duration'].mean())
    print('    Mean travel time:    ', mean_travel_time, 'seconds')
    print('                             ', seconds_to_HMS_str(mean_travel_time))
    print('*************************************************************')


# //////////////////////////////////////////////////////////////////////////////////

def user_stats(df):
    print('\nUser Stats...')

    # Display counts of user types
    user_types = df['User Type'].value_counts()
    for idx in range(len(user_types)):
        val = user_types[idx]
        user_type = user_types.index[idx]
        print('{0:21}'.format((user_type + ':')), val)

    # 'Gender' and 'Birth Year' is only available for Chicago and New York City
    # Check for these columns before attempting to access them
    if 'Gender' in df.columns:
        # Display counts of gender
        genders = df['Gender'].value_counts()
        for idx in range(len(genders)):
            val = genders[idx]
            gender = genders.index[idx]
            print('{0:21}'.format((gender + ':')), val)

    if 'Birth Year' in df.columns:
        # Display earliest, most recent, and most common year of birth
        print('Year of Birth...')
        print('Earliest:        ', int(df['Birth Year'].min()))
        print('Most recent:     ', int(df['Birth Year'].max()))
        print('Most common:     ', int(df['Birth Year'].mode()))
        print('*************************************************************')

#//////////////////////////////////////////////////////////////////////////////////////////////////////

def show_raw_data(df):

    show_rows = 5
    start = 0
    end = show_rows - 1

    print('\n Would you like to see five raw data from the current dataset?')
    while True:
        raw_data = input('(y or n):  ')
        if raw_data.lower() == 'y':
            print('\nShowing rows {} to {}:'.format(start + 1, end + 1))

            print('\n', df.iloc[start : end + 1])
            start += show_rows
            end += show_rows

            print('-----------------------------------------------------------------')
            print('\nWould you like to see the next {} rows?'.format(show_rows))
            continue
        else:
            break

# /////////////////////////////////////////////////////////////////////////////////////////////////////
def main():
    while True:
        city, month, day = get_filters()
        df = load_data(city, month, day)
        print("\n********************Data has been loaded***********************\n")

        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)
        show_raw_data(df)
        print("\n********************Required information was reported ***********************\n")

        restart = input('\nWould you like to restart? (y or n):  ')
        if restart.lower() != 'y':
            break


if __name__ == "__main__":
    main()