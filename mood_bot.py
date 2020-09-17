# mood_bot.py
import asyncio
import datetime
import mood_error as me
import os
import re
import shelve

from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
MOOD_TOKEN = os.getenv('DISCORD_TOKEN')

mood_bot = commands.Bot(command_prefix='mood_')

days_of_week = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

day_regex = re.compile(r'\b((mon|tues|wed(nes)?|thur(s)?|fri|sat(ur)?|sun)(day)?)|'
                       r'(everyday|weekend(s)?|weekday(s)?)\b', re.I)

day_dictionary = {'monday': 0, 'mon': 0, 'tuesday': 1, 'tues': 1, 'tue': 1, 'wednesday': 2, 'wednes': 2, 'wed': 2,
                  'thursday': 3, 'thurs': 3, 'thur': 3, 'friday': 4, 'fri': 4, 'saturday': 5, 'satur': 5, 'sat': 5,
                  'sunday': 6, 'sun': 6}

""" These are the preset choices for mood check-ins. """
mood_choices = ('good', 'bad', 'okay', 'meh', 'happy', 'sad', 'angry', 'upset', 'depressed', 'hungry',
                'tired', 'bored', 'irritated', 'stressed', 'frustrated', 'ashamed', 'guilty', 'worried',
                'lonely', 'prideful', 'confused', 'disgusted', 'surprised', 'disappointed')

"""Power is for switching the auto_checker ON/OFF"""
auto_checker_power_switch = 'OFF'

""" Gates are for the mood check execution; to make sure that the mood check is done in the correct order. """
date_gate = 'Open'
type_gate = 'Closed'
rating_gate = 'Closed'
why_gate = 'Closed'
stage_array = ['date', 'type', 'rating', 'explanation']

"""Repeated Strings"""
day_format_error_message = "Please enter a valid day of the week or a term like 'Everyday' or 'Weekdays' or 'Weekends'."
time_duplicate_error_message = 'Time is already in schedule.'
time_format_error_message = 'Please write time in HH:MM format.'
auto_check_input_error_message = 'Please specify whether the auto checker is ON or OFF.'
start_mood_check_message = 'Please start a mood check first.'
mood_type_error_message = "Please enter in one of the following mood types:\n" + str(mood_choices)
mood_type_message = 'You left off at the mood type.'
rating_error_message = 'Please enter an integer from 1 to 10.'
integer_message_for_diary = 'Please use integers to specify the start and end entries.'
diary_empty_message = 'Diary is empty. Please do a mood check to add an entry.'
out_of_diary_range_message_partial = 'For start and end entries, please specify integers from 1 to '

""" MOOD CALENDAR FUNCTIONS """


def num_days_to_word_days(days):
    word_days = []
    if days == [1, 1, 1, 1, 1, 1, 1]:
        word_days = 'everyday'
    elif days == [1, 1, 1, 1, 1, 0, 0]:
        word_days = 'weekdays'
    elif days == [0, 0, 0, 0, 0, 1, 1]:
        word_days = 'weekends'
    else:
        for num, day in enumerate(days):
            if day == 1:
                word_days.append(days_of_week[num])
    return word_days


async def day_format_error(context, day_input):
    await context.send(day_format_error_message)
    raise me.InputMoodError(day_format_error_message, day_input)


async def time_format_error(context, time_input):
    await context.send(time_format_error_message)
    raise me.InputMoodError(time_format_error_message, time_input)


async def duplicate_time_error(context, time_input):
    await context.send(time_duplicate_error_message)
    raise me.InputMoodError(time_duplicate_error_message, time_input)


async def new_schedule_display_message(context, days_or_times, new_sched):
    await context.send(f"The {days_or_times} in your mood schedule are now:\n{new_sched}")


@mood_bot.command(name='add_day', help='Add day(s) to mood schedule.',
                  aliases=['addday', '+day', 'day_add', 'dayadd', '+days', 'add_days', 'adddays'])
async def add_day(context, *day_inputs):
    """ This function allows the user to add a day of the week to their mood check schedule. """
    author = context.author
    [mood_days, _] = mood_schedule(author)
    for day_input in day_inputs:
        day_mo = day_regex.search(day_input)
        if day_mo is None:
            await day_format_error(context, day_input)
        else:
            if day_input.lower() == 'everyday':
                for i in range(7):
                    mood_days[i] = 1
                break
            elif day_input.lower() == 'weekdays' or day_input.lower() == 'weekday':
                for j in range(5):
                    mood_days[j] = 1
            elif day_input.lower() == 'weekends' or day_input.lower() == 'weekend':
                for k in range(5, 7):
                    mood_days[k] = 1
            else:
                mood_days[day_dictionary[day_input.lower()]] = 1
    schedule_filename = str(author) + "_mood_schedule"
    schedule_file = shelve.open(schedule_filename)
    schedule_file['days'] = mood_days
    schedule_file.close()
    await new_schedule_display_message(context, 'days', num_days_to_word_days(mood_days))


@mood_bot.command(name='add_time', help='Add time(s) (HH:MM) to mood schedule.',
                  aliases=['addtime', '+time', 'time_add', 'timeadd', 'add_times', 'addtimes', '+times'])
async def add_time(context, *time_inputs):
    """This function allows the user to add a time of day to their mood check schedule."""
    author = context.author
    [_, mood_times] = mood_schedule(author)
    for time_input in time_inputs:
        try:
            datetime.datetime.strptime(time_input, '%H:%M')
        except ValueError:
            await time_format_error(context, time_input)
        if time_input in mood_times:
            await duplicate_time_error(context, time_input)
        else:
            mood_times.append(time_input)
    times_as_datetimes = []
    for HM_time in mood_times:
        times_as_datetimes.append(datetime.datetime.strptime(HM_time, '%H:%M'))
    times_as_datetimes.sort()
    new_times = []
    for time_as_datetime in times_as_datetimes:
        new_times.append(datetime.datetime.strftime(time_as_datetime, '%H:%M'))
    schedule_filename = str(author) + "_mood_schedule"
    schedule_file = shelve.open(schedule_filename)
    schedule_file['times'] = new_times
    schedule_file.close()
    await new_schedule_display_message(context, 'times', new_times)


@mood_bot.command(name='print_schedule', help='Prints current mood check schedule.',
                  aliases=['printschedule', 'print_sched', 'printsched'])
async def print_schedule(context):
    """This function prints out the mood check-in schedule for the user in the format:
    days of the week at times of day."""
    author = context.author
    [days, times] = mood_schedule(author)
    word_days = num_days_to_word_days(days)
    await context.send("Your mood check schedule is " + str(word_days) + " at " + str(times))


@mood_bot.command(name='delete_day', help='Delete day(s) from mood check schedule.',
                  aliases=['del_day', 'delday', 'deleteday', '-day', 'del_days', 'delete_days',
                           'deldays', 'deletedays', '-days'])
async def delete_day(context, *day_inputs):
    """This function removes days from the mood check-in schedule as specified by the user."""
    author = context.author
    [mood_days, _] = mood_schedule(author)
    for day_input in day_inputs:
        day_mo = day_regex.search(day_input)
        if day_mo is None:
            await day_format_error(context, day_input)
        else:
            if day_input.lower() == 'everyday':
                for j in range(7):
                    mood_days[j] = 0
                break
            elif day_input.lower() == 'weekdays':
                for j in range(5):
                    mood_days[j] = 0
            elif day_input.lower() == 'weekends':
                for k in range(5, 7):
                    mood_days[k] = 0
            else:
                mood_days[day_dictionary[day_input.lower()]] = 0
    schedule_filename = str(author) + "_mood_schedule"
    schedule_file = shelve.open(schedule_filename)
    schedule_file['days'] = mood_days
    await new_schedule_display_message(context, 'days', num_days_to_word_days(mood_days))


async def time_not_there_error(context, mood_times, time_input):
    no_time_phrase = "Sorry, that time is not in your mood check schedule. Please choose from the following: " \
                     + str(mood_times)
    await context.send(no_time_phrase)
    raise me.InputMoodError(no_time_phrase, time_input)


@mood_bot.command(name='delete_time', help="Delete time(s) from mood check schedule. "
                                           "Enter 'all' to clear all the times from the schedule.",
                  aliases=['del_time', 'deltime', 'deletetime', '-time', 'time_del', 'time_delete',
                           'timedel', 'timedelete', 'delete_times', 'del_times', 'deletetimes', 'deltimes', '-times'])
async def delete_time(context, *time_inputs):
    """This function removes times from the mood check-in schedule as specified by the user."""
    author = context.author
    [_, mood_times] = mood_schedule(author)
    if 'all' in time_inputs:
        mood_times = []
    else:
        for time_input in time_inputs:
            try:
                datetime.datetime.strptime(time_input, '%H:%M')
            except ValueError:
                await time_format_error(context, time_input)
            if time_input not in mood_times:
                await time_not_there_error(context, mood_times, time_input)
            mood_times.remove(time_input)
    schedule_filename = str(author) + "_mood_schedule"
    schedule_file = shelve.open(schedule_filename)
    schedule_file['times'] = mood_times
    schedule_file.close()
    await new_schedule_display_message(context, 'times', mood_times)


def mood_schedule(author):
    """This function retrieves the mood schedule data (days and times) from the mood schedule file for that user."""
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


def mood_time_retriever(author):
    """This function takes the mood schedule and figures out when the next mood check will be."""
    [mood_days, mood_times] = mood_schedule(author)
    now = datetime.datetime.now()
    """returns integer 0-6 representing Monday-Sunday for today"""
    now_day = next_moodcheck_day = datetime.datetime.now().weekday()
    now_time = next_moodcheck_time = datetime.datetime.now().strftime('%H:%M:%S')  # returns current time in HH:MM:SS
    found_next_moodcheck_day = False
    next_moodcheck_date_is_set = False
    moodcheck_weekdays = []
    days_until_check = 0
    for i, day_x in enumerate(mood_days):
        if day_x == 1:
            found_next_moodcheck_day = True
            moodcheck_weekdays.append(i)  # makes a list of the weekdays that have mood checks in terms of integers 0-6
    if not found_next_moodcheck_day:
        next_datetime = 0  # there are no mood checks scheduled
    else:
        for day_y in moodcheck_weekdays:
            for time_y in mood_times:
                time_y = time_y + ':00'  # add seconds to make it the beginning of the minute only
                """checks if today is a mood check day and
                that the current time is or is before the next mood check time"""
                if day_y == now_day and time_y >= now_time:
                    next_moodcheck_date_is_set = True
                    next_moodcheck_day = day_y
                    next_moodcheck_time = time_y
                    break
        if not next_moodcheck_date_is_set:
            for day_z in moodcheck_weekdays:
                """checks if a mood check day is upcoming later in the week"""
                if day_z > now_day:
                    next_moodcheck_date_is_set = True
                    next_moodcheck_day = day_z
                    next_moodcheck_time = mood_times[0]  # sets mood check time to earliest time of the day
                    break
        if not next_moodcheck_date_is_set:  # if we still haven't found a mood check time
            for day_a in moodcheck_weekdays:
                """checks if a mood check day is upcoming next week ("earlier in the week")"""
                if day_a < now_day:
                    next_moodcheck_date_is_set = True
                    next_moodcheck_day = day_a
                    next_moodcheck_time = mood_times[0]  # sets mood check time to earliest time of the day
                    break
        if next_moodcheck_date_is_set:
            mood_hour_minute = next_moodcheck_time.split(':')
            if now_day == next_moodcheck_day:  # if there is a mood check today
                mood_date = now
            else:
                if now_day < next_moodcheck_day:  # if there is a mood check later in the week
                    days_until_check = next_moodcheck_day - now_day
                elif now_day > next_moodcheck_day:  # if there is a mood check early next week
                    days_until_check = 6 - now_day + next_moodcheck_day + 1
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


@mood_bot.command(name='next_check', help='Provides the date and time of the next mood check.')
async def next_check(context):
    """This function allows the user to call the mood_time_retriever function to
    figure out when the next mood check will be."""
    author = context.author
    check_datetime = mood_time_retriever(author)
    if check_datetime == 0:
        await context.send("There is no mood check scheduled.")
    elif auto_checker_power_switch == 'OFF':
        await context.send("There is no upcoming mood check because the auto mood checker is turned off.")
    else:
        await context.send(f"Your next mood check will be at {str(check_datetime)}")


""" MOOD CHECK FUNCTIONS """


async def auto_checker_error(context, power_switch_input):
    await context.send(auto_check_input_error_message)
    raise me.InputMoodError(auto_check_input_error_message, power_switch_input)


@mood_bot.command(name='auto', help='Turns auto mood check ON/OFF.',
                  aliases=['auto_check', 'autocheck', 'autochecker', 'auto_checker'])
async def mood_auto_checker(context, power):
    """This function waits until the next mood check is scheduled and then activates the mood check function."""
    global auto_checker_power_switch
    author = context.author
    if power.upper() == 'OFF':
        target_time = 0
        auto_checker_power_switch = power.upper()
    elif power.upper() == 'ON':
        target_time = mood_time_retriever(author)
        auto_checker_power_switch = power.upper()
    else:
        target_time = 0
        await auto_checker_error(context, power)
    if isinstance(target_time, datetime.datetime):
        while datetime.datetime.now() < target_time:
            if auto_checker_power_switch == 'OFF':
                break
            await asyncio.sleep(1)
        if auto_checker_power_switch == 'ON':
            await mood_reset(context, False)
            await mood_check(context)


@mood_bot.command(name='status', help='Reports whether mood auto checker is on or off, '
                                      'whether a mood check is in progress, '
                                      'and what stage of the mood check process is open if applicable.')
async def mood_status(context):
    await context.send(f"The auto mood checker is {auto_checker_power_switch}.")
    mood_check_status = 'has not been started.'
    if date_gate == 'Closed':
        mood_check_status = 'is in progress, '
    await context.send(f"A mood check {mood_check_status}")
    if date_gate == 'Closed':
        gate_array = [date_gate, type_gate, rating_gate, why_gate]
        await context.send(f"and is currently in the mood {stage_array[gate_array.index('Open')]} stage.")


async def time_stamp_message(context, author):
    time_stamp = mood_diary_retrieval(author, 'date', 'last_entry')
    await context.send(f"You have an unfinished mood check from {time_stamp}.")


def mood_stamp_maker(author):
    mood_stamp = mood_diary_retrieval(author, 'type', 'last_entry')
    return mood_stamp


def rating_stamp_maker(author):
    rating_stamp = mood_diary_retrieval(author, 'rating', 'last_entry')
    return rating_stamp


async def mood_rating_message(context, mood_stamp):
    await context.send(f'You left off at rating. The mood type was {mood_stamp}')


async def mood_why_message(context, mood_stamp, rating_stamp):
    await context.send(f"You left off at the explanation. The mood type was {mood_stamp} "
                       f"and the rating was {rating_stamp}.")


@mood_bot.command(name='check', help='Run a mood check.')
async def mood_check(context):
    """This function starts a mood check by recording current time and date and asking the user how they feel."""
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
        """If the date_gate isn't open, it checks to see which gate is open.
        This means that another mood check was in progress and is unfinished."""
        await time_stamp_message(context, author)
        if type_gate == 'Open':
            await context.send(mood_type_message)
        else:
            mood_stamp = mood_stamp_maker(author)
            if rating_gate == 'Open':
                await mood_rating_message(context, mood_stamp)
            elif why_gate == 'Open':
                rating_stamp = rating_stamp_maker(author)
                await mood_why_message(context, mood_stamp, rating_stamp)


async def mood_type_error(context, mood):
    await context.send(mood_type_error_message)
    raise me.InputMoodError(mood_type_error_message, mood)


@mood_bot.command(name='type')
async def mood_type_selection(context, mood_type):
    """Allows the user to answer the mood_check function with their mood selection.
    And asks the user to rate their mood from 1 to 10."""
    global type_gate, rating_gate
    author = context.author
    if type_gate == 'Open':
        if mood_type.lower() not in mood_choices:
            await mood_type_error(context, mood_type.lower())
        else:
            mood_diary_storage(author, 'type', mood_type)
            await context.send(f"On a scale from 1 to 10, how {mood_type} do you feel?\n" +
                               "Please respond by typing 'mood_rating' followed by the your selected integer.")
            type_gate = 'Closed'
            rating_gate = 'Open'
    else:
        """If the type_gate isn't open, then a mood check is either not started or is in progress.
        Checks to see which gate is open."""
        if date_gate == 'Open':
            await time_stamp_message(context, author)
        else:
            mood_stamp = mood_stamp_maker(author)
            if rating_gate == 'Open':
                await mood_rating_message(context, mood_stamp)
            elif why_gate == 'Open':
                rating_stamp = rating_stamp_maker(author)
                await mood_why_message(context, mood_stamp, rating_stamp)


async def rating_error(context, mood_rating):
    await context.send(rating_error_message)
    raise me.InputMoodError(rating_error_message, mood_rating)


@mood_bot.command(name='rating')
async def mood_rating_selection(context, mood_rating):
    """Allows user to enter their mood rating. Then, asks user to explain why they feel that way."""
    global rating_gate, why_gate
    author = context.author
    if rating_gate == 'Open':
        try:
            mood_rating = int(mood_rating)
        except ValueError:
            await rating_error(context, mood_rating)
        if mood_rating < 1 or mood_rating > 10:
            await rating_error(context, mood_rating)
        else:
            """Converts the numerical rating into words."""
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
        """If the rating_gate isn't open, then either a mood check wasn't started properly or is still in progress.
        Checks to see which gate is open."""
        if date_gate == 'Open':
            await context.send(start_mood_check_message)
        else:
            await time_stamp_message(context, author)
            if type_gate == 'Open':
                await context.send(mood_type_message)
            elif why_gate == 'Open':
                mood_stamp = mood_stamp_maker(author)
                rating_stamp = rating_stamp_maker(author)
                await mood_why_message(context, mood_stamp, rating_stamp)


@mood_bot.command(name='why', aliases=['explanation', 'explan', 'explain'])
async def mood_explanation(context, *why):
    """Allows the user to explain the reason behind their mood.
    Then, it tells the user that their mood entry has been saved (though, the data does get saved at each step.)
    The function then resets the gates so that another mood check can be started."""
    global why_gate, date_gate
    author = context.author
    if why_gate == 'Open':
        mood_diary_storage(author, 'why', why)
        await context.send("Thank you. Your mood entry has been stored.")
        why_gate = 'Closed'
        date_gate = 'Open'
    else:
        """If the why_gate is closed, then a mood check hasn't been started or is still in progress.
        Checks to see which mood gate is open."""
        if date_gate == 'Open':
            await context.send(start_mood_check_message)
        else:
            await time_stamp_message(context, author)
            if type_gate == 'Open':
                await context.send(mood_type_message)
            elif rating_gate == 'Open':
                mood_stamp = mood_stamp_maker(author)
                await mood_rating_message(context, mood_stamp)


"""MOOD DIARY FUNCTIONS"""


def mood_diary_storage(author, cat, data):
    """This function stores data to the mood diary under the appropriate category.
    Essentially, this is how mood check entries are stored."""
    diary_filename = str(author) + "_mood_diary"
    diary_file = shelve.open(diary_filename)
    if str(cat) in diary_file:
        mood_data = diary_file[str(cat)]
    else:
        mood_data = []
    mood_data.append(data)
    diary_file[str(cat)] = mood_data
    diary_file.close()


def mood_diary_retrieval(author, cat, arg):
    """This function gets entries from the mood diary to be displayed to the user via another function."""
    diary_filename = str(author) + "_mood_diary"
    diary_file = shelve.open(diary_filename)
    data_entries = diary_file[str(cat)]
    output = ''
    if arg == 'last_entry':
        last_entry = len(data_entries) - 1
        output = data_entries[last_entry]
    diary_file.close()
    return output


def mass_diary_data_storage(diary, date_data, type_data, rating_data, why_data):
    diary['date'] = date_data
    diary['type'] = type_data
    diary['rating'] = rating_data
    diary['why'] = why_data


def mass_diary_data_retrieval(diary):
    date_data = diary['date']
    type_data = diary['type']
    rating_data = diary['rating']
    why_data = diary['why']
    return date_data, type_data, rating_data, why_data


@mood_bot.command(name='count_diary', help='Tells you how many entries are in your mood diary.',
                  aliases=['diary_count', 'countdiary', 'diarycount'])
async def count_diary(context):
    """Supplies a count of how many entries are in the mood diary."""
    author = context.author
    diary_filename = str(author) + '_mood_diary'
    diary = shelve.open(diary_filename)
    if 'date' not in diary:
        context.send(diary_empty_message)
    else:
        date_data = diary['date']
        number_of_entries = len(date_data)
        if number_of_entries == 0:
            await context.send(diary_empty_message)
        elif number_of_entries == 1:
            await context.send(f'There is {str(number_of_entries)} entry in the mood diary.')
            await context.send(f'This entry was on {str(date_data[0])}.')
        else:
            await context.send(f'There are {str(number_of_entries)} entries in the mood diary.')
            await context.send(f'The first entry was on {str(date_data[0])} '
                               f'and the last entry was on {str(date_data[number_of_entries - 1])}')
    diary.close()


async def diary_integer_error(context, start, end):
    await context.send(integer_message_for_diary)
    raise me.InputMoodError(integer_message_for_diary, [start, end])


async def diary_range_error(context, start, end, number_of_entries):
    out_of_diary_range_message_full = out_of_diary_range_message_partial + str(number_of_entries) + '.'
    await context.send(out_of_diary_range_message_full)
    raise me.InputMoodError(out_of_diary_range_message_full, [start, end])


@mood_bot.command(name='print_diary', help="Prints out entries from the mood diary. "
                                           "User specifies the start and end entries "
                                           "or specifies 'all' for all entries.",
                  aliases=['diary_print', 'printdiary', 'diaryprint'])
async def print_diary(context, start='all', end='0'):
    """Prints out the mood diary as specified by the user.
    User can either write 'all' for all entries, or can specify start and end entries."""
    author = context.author
    diary_filename = str(author) + '_mood_diary'
    diary = shelve.open(diary_filename)
    if 'date' not in diary:
        await context.send(diary_empty_message)
    else:
        diary.close()  # so that we don't try opening the diary file twice, concurrently
        await mood_reset(context, False)  # makes sure that all the data is the same length
        diary = shelve.open(diary_filename)
        [date_data, type_data, rating_data, why_data] = mass_diary_data_retrieval(diary)
        number_of_entries = len(date_data)
        if start.lower() == 'all':
            start = 1
            end = number_of_entries
        try:
            start = int(start)
            end = int(end)
        except ValueError:
            diary.close()
            await diary_integer_error(context, start, end)
        if start < 1 or end > number_of_entries:
            await diary_range_error(context, start, end, number_of_entries)
        else:
            start = start - 1
            for j in range(start, end):
                entry = [str(date_data[j]), str(type_data[j]), str(rating_data[j]), str(why_data[j])]
                why_string = entry[3]
                why_string = str(why_string)
                why_string = why_string.replace(',', '')
                why_string = why_string.replace('(', '')
                why_string = why_string.replace(')', '')
                why_string = why_string.replace("'", '')
                entry[3] = why_string
                await context.send(' '.join(entry))
    diary.close()


@mood_bot.command(name='del_diary', help="Delete entries from the diary. User specifies the start and end entries, or "
                                         "specifies 'all' to delete all entries.",
                  aliases=['delete_diary', 'deletediary', 'diary_del', 'diarydel', 'diarydelete', 'diary_delete'])
async def delete_diary(context, start, end='0'):
    """User can remove entries from the mood diary, by specifying all entries or start and end entries."""
    author = context.author
    diary_filename = str(author) + '_mood_diary'
    diary = shelve.open(diary_filename)
    if 'date' not in diary:
        await context.send(diary_empty_message)
    else:
        diary.close()  # so that we don't try opening the diary file twice, concurrently
        await mood_reset(context, False)  # makes sure that all the data is the same length
        diary = shelve.open(diary_filename)
        [date_data, type_data, rating_data, why_data] = mass_diary_data_retrieval(diary)
        number_of_entries = len(date_data)
        if start.lower() == 'all':
            start = 1
            end = number_of_entries
        try:
            start = int(start)
            end = int(end)
        except ValueError:
            diary.close()
            await diary_integer_error(context, start, end)
        if start < 1 or end > number_of_entries:
            await diary_range_error(context, start, end, number_of_entries)
        else:
            start = start - 1
            for k in range(start, end):
                del date_data[k]
                del type_data[k]
                del rating_data[k]
                del why_data[k]
            mass_diary_data_storage(diary, date_data, type_data, rating_data, why_data)
            await context.send('Your specified entries have been successfully deleted.')
    diary.close()


@mood_bot.command(name='reset', help='Start over a mood check.')
async def mood_reset(context, manual=True):
    """Reset function: deletes any extra entries in the diary and
    sets all the gates to closed save for the date_gate which will be set to open."""
    global date_gate, type_gate, rating_gate, why_gate
    author = context.author
    diary_filename = str(author) + "_mood_diary"
    diary = shelve.open(diary_filename)
    data_cats = [date_data, type_data, rating_data, why_data] = mass_diary_data_retrieval(diary)
    data_lengths = [len(date_data), len(type_data), len(rating_data), len(why_data)]
    if data_lengths[0] == data_lengths[1] == data_lengths[2] == data_lengths[3]:
        if manual:
            await context.send(f'Mood checking does not need to be reset for {str(author)}.')
        diary.close()
    else:
        shortest_length = min(data_lengths)
        for cat in data_cats:
            while len(cat) > shortest_length:
                del cat[len(cat) - 1]
        mass_diary_data_storage(diary, date_data, type_data, rating_data, why_data)
        diary.close()
        date_gate = 'Open'
        type_gate = 'Closed'
        rating_gate = 'Closed'
        why_gate = 'Closed'
        if manual:
            await context.send(f'Mood checking has been reset for {str(author)}. You can now start a new mood check.')


mood_bot.run(MOOD_TOKEN)
