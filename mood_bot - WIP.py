# mood_bot.py
import asyncio
import datetime
import os
import re
import shelve

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

mood_bot = commands.Bot(command_prefix='mood_')

days_of_week = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
# These are the preset choices for mood check-ins.
mood_choices = ('good', 'bad', 'okay', 'meh', 'happy', 'sad', 'angry', 'upset', 'depressed', 'hungry',
                'tired', 'bored', 'irritated', 'stressed', 'frustrated', 'ashamed', 'guilty', 'worried',
                'lonely', 'prideful', 'confused', 'disgusted', 'surprised', 'disappointed')

# Gates are for the mood check execution
# to make sure that the mood check is done in the correct order.
date_gate = 'Open'
type_gate = 'Closed'
rating_gate = 'Closed'
why_gate = 'Closed'


# MOOD CALENDAR FUNCTIONS

# This function allows the user to add a day of the week to their mood check schedule.
@mood_bot.command(name='add_day', help='Add day(s) to mood schedule.',
                  aliases=['addday', '+day', 'day_add', 'dayadd', '+days', 'add_days', 'adddays'])
async def add_day(context, *days):
    day_regex = re.compile(r'\b((mon|tues|wed(nes)?|thur(s)?|fri|sat(ur)?|sun)(day)?)|'
                           r'(everyday|weekend(s)?|weekday(s)?)\b', re.I)
    for day_x in days:
        day_mo = day_regex.search(day_x)
        if day_mo is None:
            await context.send("Please enter a valid day of the week or a "
                               "term like 'Everyday' or 'Weekdays' or 'Weekends'.")
            return
    author = context.author
    [mood_days, _] = mood_schedule(author)
    for day_y in days:
        if day_y.lower() == 'everyday':
            for k in range(7):
                mood_days[k] = 1
            break
        elif day_y.lower() == 'weekdays' or day_y.lower() == 'weekday':
            for j in range(5):
                mood_days[j] = 1
        elif day_y.lower() == 'weekends' or day_y.lower() == 'weekend':
            for k in range(5, 7):
                mood_days[k] = 1
        else:
            if day_y.lower() == 'mon' or day_y.lower() == 'monday':
                mood_days[0] = 1
            elif day_y.lower() == 'tues' or day_y.lower() == 'tuesday':
                mood_days[1] = 1
            elif day_y.lower() == 'wed' or day_y.lower() == 'wednes' or day_y.lower() == 'wednesday':
                mood_days[2] = 1
            elif day_y.lower() == 'thur' or day_y.lower() == 'thurs' or day_y.lower() == 'thursday':
                mood_days[3] = 1
            elif day_y.lower() == 'fri' or day_y.lower() == 'friday':
                mood_days[4] = 1
            elif day_y.lower() == 'sat' or day_y.lower() == 'satur' or day_y.lower == 'saturday':
                mood_days[5] = 1
            elif day_y.lower() == 'sun' or day_y.lower() == 'sunday':
                mood_days[6] = 1
    schedule_filename = str(author) + "_mood_schedule"
    schedule_file = shelve.open(schedule_filename)
    schedule_file['days'] = mood_days
    schedule_file.close()


# This function allows the user to add a time of day to their mood check schedule.
@mood_bot.command(name='add_time', help='Add time(s) (HH:MM) to mood schedule.',
                  aliases=['addtime', '+time', 'time_add', 'timeadd', 'add_times', 'addtimes', '+times'])
async def add_time(context, *ts):
    for t in ts:
        try:
            datetime.datetime.strptime(t, '%H:%M')
        except ValueError:
            await context.send("Please write time in HH:MM format.")
            return
    author = context.author
    [_, mood_times] = mood_schedule(author)
    for t in ts:
        if t in mood_times:
            await context.send("Time is already in schedule.")
            return
    for t in ts:
        mood_times.append(t)
    times_as_datetimes = []
    try:
        for i in mood_times:
            times_as_datetimes.append(datetime.datetime.strptime(i, '%H:%M'))
    except ValueError:
        pass
    times_as_datetimes.sort()
    new_times = []
    for j in times_as_datetimes:
        new_times.append(datetime.datetime.strftime(j, '%H:%M'))
    schedule_filename = str(author) + "_mood_schedule"
    schedule_file = shelve.open(schedule_filename)
    schedule_file['times'] = new_times
    schedule_file.close()


# This function prints out the mood check-in schedule for the user in the format: days of the week at times of day.
@mood_bot.command(name='print_schedule', help='Prints current mood check schedule.',
                  aliases=['printschedule', 'print_sched', 'printsched'])
async def print_schedule(context):
    author = context.author
    [days, times] = mood_schedule(author)
    word_days = []
    if days == [1, 1, 1, 1, 1, 1, 1]:
        word_days = 'everyday'
    elif days == [1, 1, 1, 1, 1, 0, 0]:
        word_days = 'weekdays'
    elif days == [0, 0, 0, 0, 0, 1, 1]:
        word_days = 'weekends'
    else:
        for j, day in enumerate(days):
            if day == 1:
                word_days.append(days_of_week[j])
    await context.send("Your mood check schedule is " + str(word_days) + " at " + str(times))


# This function removes days from the mood check-in schedule as specified by the user.
@mood_bot.command(name='delete_day', help='Delete day(s) from mood check schedule.',
                  aliases=['del_day', 'delday', 'deleteday', '-day', 'del_days', 'delete_days',
                           'deldays', 'deletedays', '-days'])
async def delete_day(context, *days):
    day_regex = re.compile(r'\b((mon|tues|wed(nes)?|thur(s)?|fri|sat(ur)?|sun)(day)?)|'
                           r'(everyday|weekend(s)?|weekday(s)?)\b', re.I)
    for day_x in days:
        day_mo = day_regex.search(day_x)
        if day_mo is None:
            await context.send("Please enter a valid day of the week or a "
                               "term like 'Everyday' or 'Weekdays' or 'Weekends'.")
            return
    author = context.author
    [mood_days, _] = mood_schedule(author)
    for day_y in days:
        if day_y.lower() == 'everyday':
            for j in range(7):
                mood_days[j] = 0
            break
        elif day_y.lower() == 'weekdays':
            for j in range(5):
                mood_days[j] = 0
        elif day_y.lower() == 'weekends':
            for k in range(5, 7):
                mood_days[k] = 0
        else:
            if day_y.lower() == 'mon' or day_y.lower() == 'monday':
                mood_days[0] = 0
            elif day_y.lower() == 'tues' or day_y.lower() == 'tuesday':
                mood_days[1] = 0
            elif day_y.lower() == 'wed' or day_y.lower() == 'wednes' or day_y.lower() == 'wednesday':
                mood_days[2] = 0
            elif day_y.lower() == 'thur' or day_y.lower() == 'thurs' or day_y.lower() == 'thursday':
                mood_days[3] = 0
            elif day_y.lower() == 'fri' or day_y.lower() == 'friday':
                mood_days[4] = 0
            elif day_y.lower() == 'sat' or day_y.lower() == 'satur' or day_y.lower == 'saturday':
                mood_days[5] = 0
            elif day_y.lower() == 'sun' or day_y.lower() == 'sunday':
                mood_days[6] = 0
            else:
                word_days = []
                for j, day_z in enumerate(mood_days):
                    if day_z == 1:
                        word_days.append(days_of_week[j])
                await context.send("Sorry, that day is not in your mood check schedule. "
                                   "Please choose from the following: " + str(word_days))
                break
    schedule_filename = str(author) + "_mood_schedule"
    schedule_file = shelve.open(schedule_filename)
    schedule_file['days'] = mood_days


# This function removes times from the mood check-in schedule as specified by the user.
@mood_bot.command(name='delete_time', help='Delete time(s) from mood check schedule.',
                  aliases=['del_time', 'deltime', 'deletetime', '-time', 'time_del', 'time_delete',
                           'timedel', 'timedelete', 'delete_times', 'del_times', 'deletetimes', 'deltimes', '-times'])
async def delete_time(context, *ts):
    for t in ts:
        try:
            datetime.datetime.strptime(t, '%H:%M')
        except ValueError:
            await context.send("Please write time in HH:MM format.")
            return
    author = context.author
    [_, mood_times] = mood_schedule(author)
    for t in ts:
        if t not in mood_times:
            await context.send("Sorry, that time is not in your mood check schedule. "
                               "Please choose from the following: " + str(mood_times))
            return
    for t in ts:
        mood_times.remove(t)
    schedule_filename = str(author) + "_mood_schedule"
    schedule_file = shelve.open(schedule_filename)
    schedule_file['times'] = mood_times
    schedule_file.close()


# This function retrieves the mood schedule data (days and times) from the mood schedule file for that user.
def mood_schedule(author):
    schedule_filename = str(author) + "_mood_schedule"
    if not os.path.exists(schedule_filename + ".dat"):
        mood_days = [0, 0, 0, 0, 0, 0, 0]
        mood_times = []
    else:
        schedule_file = shelve.open(schedule_filename)
        if 'days' in schedule_file:
            mood_days = schedule_file['days']
        else:
            mood_days = [0, 0, 0, 0, 0, 0, 0]
        if 'times' in schedule_file:
            mood_times = schedule_file['times']
        else:
            mood_times = []
        schedule_file.close()
    return mood_days, mood_times


# This function takes the mood schedule and figures out when the next mood check will be.
def mood_time_retriever(author):
    [mood_days, mood_times] = mood_schedule(author)
    now = datetime.datetime.now()
    now_day = next_day = datetime.datetime.now().weekday()  # returns integer 0-6 representing Monday-Sunday for today
    now_time = next_time = datetime.datetime.now().strftime('%H:%M:%S')  # returns current time in HH:MM
    found_day = False  # did we find the next mood day?
    next_date_is_set = False  # did we schedule the next mood check?
    mood_weekdays = []
    days_until_check = 0
    for i, day_x in enumerate(mood_days):
        if day_x == 1:
            found_day = True
            mood_weekdays.append(i)  # makes a list of the weekdays that have mood checks in terms of integers 0-6
    if not found_day:
        next_datetime = 0  # there are no mood checks scheduled
    else:
        for day_y in mood_weekdays:
            for time_y in mood_times:
                time_y = time_y + ':00'  # add seconds to make it the beginning of the minute only
                # checks if today is a mood check day and
                # that the current time is or is before the next mood check time
                if day_y == now_day and time_y >= now_time:
                    next_date_is_set = True
                    next_day = day_y
                    next_time = time_y
                    break
        if not next_date_is_set:
            for day_z in mood_weekdays:
                # checks if a mood check day is upcoming later in the week
                if day_z > now_day:
                    next_date_is_set = True
                    next_day = day_z
                    next_time = mood_times[0]  # sets mood check time to earliest time of the day
                    break
        if not next_date_is_set:  # if we still haven't found a mood check time
            for day_a in mood_weekdays:
                # checks if a mood check day is upcoming next week ("earlier in the week")
                if day_a < now_day:
                    next_date_is_set = True
                    next_day = day_a
                    next_time = mood_times[0]  # sets mood check time to earliest time of the day
                    break
        if next_date_is_set:
            mood_hour_minute = next_time.split(':')
            if now_day == next_day:  # if there is a mood check today
                mood_date = now
            else:
                if now_day < next_day:  # if there is a mood check later in the week
                    days_until_check = next_day - now_day
                elif now_day > next_day:  # if there is a mood check early next week
                    days_until_check = 6 - now_day + next_day + 1
                days_delta = datetime.timedelta(days=days_until_check)
                mood_date = now + days_delta
            mood_year = mood_date.year
            mood_month = mood_date.month
            mood_day = mood_date.day
            next_datetime = datetime.datetime(mood_year, mood_month, mood_day, int(mood_hour_minute[0]),
                                              int(mood_hour_minute[1]), 0)
        else:
            next_datetime = 0
    return next_datetime


# This function allows the user to call the mood_time_retriever function to figure out when the next mood check will be.
@mood_bot.command(name='next_check', help='Provides the date and time of the next mood check.')
async def next_check(context):
    author = context.author
    check_datetime = mood_time_retriever(author)
    if check_datetime == 0:
        await context.send("There is no mood check scheduled.")
    else:
        await context.send(f"Your next mood check will be at {str(check_datetime)}")


# MOOD CHECK FUNCTIONS


# This function waits until the next mood check is scheduled and then activates the mood check function.
@mood_bot.command(name='auto', help='Turns auto mood check ON/OFF.',
                  aliases=['auto_check', 'autocheck', 'autochecker', 'auto_checker'])
async def mood_auto_checker(context, power='OFF'):
    author = context.author
    if power.upper() == 'OFF':
        target_time = 0
    elif power.upper() == 'ON':
        target_time = mood_time_retriever(author)
    else:
        target_time = 0
        await context.send('Please specify whether the auto checker is ON or OFF.')
    if isinstance(target_time, datetime.datetime):
        while datetime.datetime.now() < target_time:
            if power.upper() == 'OFF':
                break
            await asyncio.sleep(1)
        if power.upper() == 'ON':
            await mood_check(context)


# This function stores data to the mood diary under the appropriate category.
# Essentially, this is how mood check entries are stored.
def mood_diary_storage(author, cat, data):
    diary_filename = str(author) + "_mood_diary"
    diary_file = shelve.open(diary_filename)
    if str(cat) in diary_file:
        mood_data = diary_file[str(cat)]
    else:
        mood_data = []
    mood_data.append(data)
    diary_file[str(cat)] = mood_data
    diary_file.close()


# This function gets entries from the mood diary to be displayed to the user via another function.
def mood_diary_retrieval(author, cat, arg):
    diary_filename = str(author) + "_mood_diary"
    diary_file = shelve.open(diary_filename)
    data_entries = diary_file[str(cat)]
    output = ''
    if arg == 'last_entry':
        last_entry = len(data_entries) - 1
        output = data_entries[last_entry]
    diary_file.close()
    return output


# This function starts a mood check by recording current time and date and asking the user how they feel.
@mood_bot.command(name='check', help='Run a mood check.')
async def mood_check(context):
    global date_gate, type_gate
    author = context.author
    if date_gate == 'Open':
        entry_time = datetime.datetime.now()
        mood_diary_storage(author, 'date', entry_time.strftime('%Y/%m/%d %H:%M:%S'))
        await context.send("How are you feeling, " + str(author) + "?\n" +
                           "Please select from the following mood types:\n" +
                           str(mood_choices) + "\n" +
                           "Please respond by typing 'mood_type' followed by your selected mood.")
        date_gate = 'Closed'
        type_gate = 'Open'
    else:
        # If the date_gate isn't open, it checks to see which gate is open.
        # This means that another mood check was in progress and is unfinished.
        time_stamp = mood_diary_retrieval(author, 'date', 'last_entry')
        await context.send(f"You have an unfinished mood check from {time_stamp}.")
        if type_gate == 'Open':
            await context.send('You left off at the mood type.')
        else:
            mood_stamp = mood_diary_retrieval(author, 'type', 'last_entry')
            if rating_gate == 'Open':
                await context.send(f"You left off at the rating. The mood type was {mood_stamp}.")
            elif why_gate == 'Open':
                rating_stamp = mood_diary_retrieval(author, 'rating', 'last_entry')
                await context.send(f"You left off at the explanation. The mood type was {mood_stamp} "
                                   f"and the rating was {rating_stamp}.")
            else:
                await context.send('An unexpected error occurred.')
                raise


# Allows the user to answer the mood_check function with their mood selection.
# And asks the user to rate their mood from 1 to 10.
@mood_bot.command(name='type')
async def mood_type_selection(context, mood_type):
    global type_gate, rating_gate
    author = context.author
    if type_gate == 'Open':
        if mood_type.lower() not in mood_choices:
            await context.send("Sorry, I didn't quite get that. " +
                               "Please enter in one of the following mood types:\n" + str(mood_choices))
        else:
            mood_diary_storage(author, 'type', mood_type)
            await context.send(f"On a scale from 1 to 10, how {mood_type} do you feel?\n" +
                               "Please respond by typing 'mood_rating' followed by the your selected integer.")
            type_gate = 'Closed'
            rating_gate = 'Open'
    else:
        # If the type_gate isn't open, then a mood check is either not started or is in progress.
        # Checks to see which gate is open.
        if date_gate == 'Open':
            await context.send('Please start a mood_check first.')
        else:
            time_stamp = mood_diary_retrieval(author, 'date', 'last_entry')
            await context.send(f"You have an unfinished mood check from {time_stamp}.")
            mood_stamp = mood_diary_retrieval(author, 'type', 'last_entry')
            if rating_gate == 'Open':
                await context.send(f'You left off at rating. The mood type was {mood_stamp}')
            elif why_gate == 'Open':
                rating_stamp = mood_diary_retrieval(author, 'rating', 'last_entry')
                await context.send(f'You left off at explanation. The mood type was {mood_stamp} and '
                                   f'the mood rating was {rating_stamp}.')
            else:
                await context.send('An unexpected error occurred.')
                raise


# Allows user to enter their mood rating. Then, asks user to explain why they feel that way.
@mood_bot.command(name='rating')
async def mood_rating_selection(context, mood_rating):
    global rating_gate, why_gate
    author = context.author
    if rating_gate == 'Open':
        try:
            mood_rating = int(mood_rating)
        except ValueError:
            await context.send("Please enter an integer from 1 to 10.")
            return
        if mood_rating < 1 or mood_rating > 10:
            await context.send("Please enter an integer from 1 to 10.")
        else:
            # Converts the numerical rating into words.
            if mood_rating <= 2:
                qualifier = 'a tad'
            elif mood_rating <= 4:
                qualifier = 'kind of'
            elif mood_rating <= 6:
                qualifier = 'somewhat'
            elif mood_rating <= 8:
                qualifier = 'mostly'
            else:
                qualifier = 'extremely'
            mood_diary_storage(author, 'rating', mood_rating)
            mood_type = mood_diary_retrieval(author, 'type', 'last_entry')
            await context.send(f"{str(author)}, why do you feel {qualifier} {mood_type}?\n" +
                               "Please respond by typing 'mood_why' followed by your explanation.")
            rating_gate = 'Closed'
            why_gate = 'Open'
    else:
        # If the rating_gate isn't open, then either a mood check wasn't started properly or is still in progress.
        # Checks to see which gate is open.
        if date_gate == 'Open':
            await context.send('Please start a mood check first.')
        else:
            time_stamp = mood_diary_retrieval(author, 'date', 'last_entry')
            await context.send(f"You have an unfinished mood check from {time_stamp}.")
            if type_gate == 'Open':
                await context.send('You left off at the mood type.')
            elif why_gate == 'Open':
                mood_stamp = mood_diary_retrieval(author, 'type', 'last_entry')
                rating_stamp = mood_diary_retrieval(author, 'rating', 'last_entry')
                await context.send(f'You left off at the explanation. The mood type was {mood_stamp} and '
                                   f'and the mood rating was {rating_stamp}.')
            else:
                await context.send('An unexpected error occurred.')
                raise


# Allows the user to explain the reason behind their mood.
# Then, it tells the user that their mood entry has been saved (though, the data does get saved at each step.)
# The function then resets the gates so that another mood check can be started.
@mood_bot.command(name='why', aliases=['explanation', 'explan', 'explain'])
async def mood_explanation(context, *why):
    global why_gate, date_gate
    author = context.author
    if why_gate == 'Open':
        mood_diary_storage(author, 'why', why)
        await context.send("Thank you. Your mood entry has been stored.")
        why_gate = 'Closed'
        date_gate = 'Open'
    else:
        # If the why_gate is closed, then a mood check hasn't been started or is still in progress.
        # Checks to see which mood gate is open.
        if date_gate == 'Open':
            await context.send('Please start a mood check first.')
        else:
            time_stamp = mood_diary_retrieval(author, 'date', 'last_entry')
            await context.send(f"You have an unfinished mood check from {time_stamp}.")
            if type_gate == 'Open':
                await context.send('You left off at the mood type.')
            elif rating_gate == 'Open':
                mood_stamp = mood_diary_retrieval(author, 'type', 'last_entry')
                await context.send(f'You left off at rating. The mood type was {mood_stamp}')
            else:
                await context.send('An unexpected error occurred.')
                raise


# Supplies a count of how many entries are in the mood diary.
@mood_bot.command(name='count_diary', help='Tells you how many entries are in your mood diary. ')
async def count_diary(context):
    author = context.author
    diary_filename = str(author) + '_mood_diary'
    d = shelve.open(diary_filename)
    if 'date' not in d:
        context.send('Diary is empty. Please do a mood check to add an entry.')
    else:
        date_data = d['date']
        number_of_entries = len(date_data)
        if number_of_entries == 1:
            await context.send(f'There is {str(number_of_entries)} entry in the mood diary.')
            await context.send(f'This entry was on {str(date_data[0])}.')
        else:
            await context.send(f'There are {str(number_of_entries)} entries in the mood diary.')
            await context.send(f'The first entry was on {str(date_data[0])} '
                               f'and the last entry was on {str(date_data[number_of_entries - 1])}')
    d.close()


# Prints out the mood diary as specified by the user.
# User can either write 'all' for all entries, or can specify start and end entries.
@mood_bot.command(name='print_diary', help="Prints out entries from the mood diary. "
                                           "User specifies the start and end entries "
                                           "or specifies 'all' for all entries.",
                  aliases=['diary_print', 'printdiary', 'diaryprint'])
async def print_diary(context, start, end='0'):
    author = context.author
    diary_filename = str(author) + '_mood_diary'
    d = shelve.open(diary_filename)
    if 'date' not in d:
        await context.send('Diary is empty. Please do a mood check to add an entry.')
    else:
        d.close()  # so that we don't try opening the diary file twice, concurrently
        await mood_reset(context, False)  # makes sure that all the data is the same length
        d = shelve.open(diary_filename)
        date_data = d['date']
        type_data = d['type']
        rating_data = d['rating']
        why_data = d['why']
        number_of_entries = len(date_data)
        if start.lower() == 'all':
            start = 1
            end = number_of_entries
        try:
            start = int(start)
            end = int(end)
        except ValueError:
            await context.send('Please use integers to specify the start and end entries.')
            d.close()
            return
        if start < 1 or end > number_of_entries:
            await context.send(f'For start and end entries, please specify integers from 1 to {number_of_entries}.')
        else:
            start = start - 1
            for j in range(start, end):
                entry = [str(date_data[j]), str(type_data[j]), str(rating_data[j]), str(why_data[j])]
                s = entry[3]
                s = str(s)
                s = s.replace(',', '')
                s = s.replace('(', '')
                s = s.replace(')', '')
                s = s.replace("'", '')
                entry[3] = s
                await context.send(' '.join(entry))
    d.close()


# User can remove entries from the mood diary, by specifying all entries or start and end entries.
@mood_bot.command(name='del_diary', help="Delete entries from the diary. User specifies the start and end entries, or "
                                         "specifies 'all' to delete all entries.",
                  aliases=['delete_diary', 'deletediary', 'diary_del', 'diarydel', 'diarydelete', 'diary_delete'])
async def delete_diary(context, start, end='0'):
    author = context.author
    diary_filename = str(author) + '_mood_diary'
    d = shelve.open(diary_filename)
    if 'date' not in d:
        await context.send('Diary is empty. There are no entries to delete.')
    else:
        d.close()  # so that we don't try opening the diary file twice, concurrently
        await mood_reset(context, False)  # makes sure that all the data is the same length
        d = shelve.open(diary_filename)
        date_data = d['date']
        type_data = d['type']
        rating_data = d['rating']
        why_data = d['why']
        number_of_entries = len(date_data)
        if start.lower() == 'all':
            start = 1
            end = number_of_entries
        try:
            start = int(start)
            end = int(end)
        except ValueError:
            await context.send('Please use integers to specify the start and end entries.')
            d.close()
            return
        if start < 1 or end > number_of_entries:
            await context.send(f'For start and end entries, please specify integers from 1 to {number_of_entries}.')
        else:
            start = start - 1
            for k in range(start, end):
                del date_data[k]
                del type_data[k]
                del rating_data[k]
                del why_data[k]
            d['date'] = date_data
            d['type'] = type_data
            d['rating'] = rating_data
            d['why'] = why_data
            await context.send('Your specified entries have been successfully deleted.')
    d.close()


# Reset function: deletes any extra entries in the diary and
#  sets all the gates to closed save for the date_gate which will be set to open.
@mood_bot.command(name='reset', help='Start over a mood check.')
async def mood_reset(context, manual=True):
    global date_gate, type_gate, rating_gate, why_gate
    author = context.author
    diary_filename = str(author) + "_mood_diary"
    d = shelve.open(diary_filename)
    date_data = d['date']
    type_data = d['type']
    rating_data = d['rating']
    why_data = d['why']
    data_cats = [date_data, type_data, rating_data, why_data]
    data_lengths = [len(date_data), len(type_data), len(rating_data), len(why_data)]
    if data_lengths[0] == data_lengths[1] == data_lengths[2] == data_lengths[3]:
        if manual:
            await context.send(f'mood_bot does not need to be reset for {str(author)}.')
        d.close()
        return
    shortest_length = min(data_lengths)
    for cat in data_cats:
        while len(cat) > shortest_length:
            del cat[len(cat) - 1]
    d['date'] = date_data
    d['type'] = type_data
    d['rating'] = rating_data
    d['why'] = why_data
    d.close()
    date_gate = 'Open'
    type_gate = 'Closed'
    rating_gate = 'Closed'
    why_gate = 'Closed'
    if manual:
        await context.send(f'mood_bot has been reset for {str(author)}. You can now start a new mood check.')


mood_bot.run(TOKEN)
