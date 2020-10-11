# mood_bot.py
import asyncio
import datetime
import mood_constant as m_const
import mood_error as m_error
import os
import shelve
import schedule_constant as sched_const

from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
MOOD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_TOKEN = os.getenv('GUILD_TOKEN')
nick_username = 'NiKnight#2745'

mood_bot = commands.Bot(command_prefix='mood_')


""" Stage(s) are for the mood check execution; to make sure that the mood check is done in the correct order. """
stage_array = ('date', 'type', 'rating', 'explanation')

"""ERROR MESSAGE FUNCTIONS"""


async def day_format_error(context, day_input):
    await context.send(m_const.DAY_FORMAT_ERROR_MESSAGE)
    raise m_error.InputMoodError(m_const.DAY_FORMAT_ERROR_MESSAGE, day_input)


async def time_format_error(context, time_input):
    await context.send(m_const.TIME_FORMAT_ERROR_MESSAGE)
    raise m_error.InputMoodError(m_const.TIME_FORMAT_ERROR_MESSAGE, time_input)


async def duplicate_time_error(context, time_input):
    await context.send(m_const.TIME_DUPLICATE_ERROR_MESSAGE)
    raise m_error.InputMoodError(m_const.TIME_DUPLICATE_ERROR_MESSAGE, time_input)


async def time_not_there_error(context, mood_times, time_input):
    no_time_phrase = m_const.NO_TIME_ERROR_MESSAGE + str(mood_times)
    await context.send(no_time_phrase)
    raise m_error.InputMoodError(no_time_phrase, time_input)


async def auto_checker_error(context, power_switch_input):
    await context.send(m_const.AUTO_CHECK_INPUT_ERROR_MESSAGE)
    raise m_error.InputMoodError(m_const.AUTO_CHECK_INPUT_ERROR_MESSAGE, power_switch_input)


async def time_stamp_message(context, author):
    time_stamp = mood_diary_retrieval(author, 'date', 'last_entry')
    await context.send(m_const.UNFINISHED_MOOD_CHECK_MESSAGE % time_stamp)


async def mood_type_error(context, mood):
    await context.send(m_const.MOOD_TYPE_ERROR_MESSAGE)
    raise m_error.InputMoodError(m_const.MOOD_TYPE_ERROR_MESSAGE, mood)


async def rating_error(context, mood_rating):
    await context.send(m_const.RATING_ERROR_MESSAGE)
    raise m_error.InputMoodError(m_const.RATING_ERROR_MESSAGE, mood_rating)


async def diary_integer_error(context, start, end):
    await context.send(m_const.INTEGER_MESSAGE_FOR_DIARY)
    raise m_error.InputMoodError(m_const.INTEGER_MESSAGE_FOR_DIARY, [start, end])


async def diary_range_error(context, start, end, number_of_entries):
    out_of_diary_range_message_full = m_const.OUT_OF_DIARY_RANGE_MESSAGE % str(number_of_entries)
    await context.send(out_of_diary_range_message_full)
    raise m_error.InputMoodError(out_of_diary_range_message_full, [start, end])


""" MOOD CALENDAR FUNCTIONS """


def bool_days_to_word_days(days):
    word_days = []
    if days == [True, True, True, True, True, True, True]:
        word_days = 'everyday'
    elif days == [True, True, True, True, True, False, False]:
        word_days = 'weekdays'
    elif days == [False, False, False, False, False, True, True]:
        word_days = 'weekends'
    else:
        for num, day in enumerate(days):
            if day:
                word_days.append(sched_const.DAYS_OF_WEEK[num])
    return word_days


def mood_schedule_retrieval(author):
    """This function retrieves the mood schedule data (days and times) from the mood schedule file for that user."""
    mood_filename = str(author) + "_moodfile"
    if not os.path.exists(mood_filename + ".dat"):
        mood_days = [False, False, False, False, False, False, False]
        mood_times = []
    else:
        schedule = shelve.open(mood_filename)
        if 'days' in schedule:
            mood_days = schedule['days']
        else:
            mood_days = [False, False, False, False, False, False, False]
        if 'times' in schedule:
            mood_times = schedule['times']
        else:
            mood_times = []
        schedule.close()
    return mood_days, mood_times


def mood_schedule_storage(author, days_or_times_string, value):
    """This function stores days and times to the mood file."""
    mood_filename = str(author) + "_moodfile"
    schedule = shelve.open(mood_filename)
    schedule[str(days_or_times_string)] = value
    schedule.close()


@mood_bot.command(name='add_day', help='Add day(s) to mood schedule.',
                  aliases=['addday', '+day', 'day_add', 'dayadd', '+days', 'add_days', 'adddays', 'day+', 'days+'])
async def add_day(context, *day_inputs):
    """ This function allows the user to add a day of the week to their mood check schedule. """
    author = context.author
    [mood_days, _] = mood_schedule_retrieval(author)
    day_inputs_lower = list(map(lambda x: x.lower(), day_inputs))
    for day_input_y in day_inputs_lower:
        day_mo = sched_const.DAY_REGEX.search(day_input_y)
        if day_mo is None:
            await day_format_error(context, day_input_y)
        else:
            if day_input_y == 'everyday':
                for i in range(7):
                    mood_days[i] = True
                break
            elif day_input_y == 'weekdays' or day_input_y == 'weekday':
                for j in range(5):
                    mood_days[j] = True
            elif day_input_y == 'weekends' or day_input_y == 'weekend':
                for k in range(5, 7):
                    mood_days[k] = True
            else:
                mood_days[sched_const.DAY_DICTIONARY[day_input_y]] = True
    mood_schedule_storage(author, 'days', mood_days)
    await context.send(m_const.NEW_SCHEDULE_MESSAGE % ('days', bool_days_to_word_days(mood_days)))


@mood_bot.command(name='add_time', help='Add time(s) (HH:MM) to mood schedule.',
                  aliases=['addtime', '+time', 'time_add', 'timeadd', 'add_times', 'addtimes', '+times', 'time+',
                           'times+'])
async def add_time(context, *time_inputs):
    """This function allows the user to add a time of day to their mood check schedule."""
    author = context.author
    [_, mood_times] = mood_schedule_retrieval(author)
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
    mood_schedule_storage(author, 'times', new_times)
    await context.send(m_const.NEW_SCHEDULE_MESSAGE % ('times', new_times))


@mood_bot.command(name='print_schedule', help='Prints current mood check schedule.',
                  aliases=['printschedule', 'print_sched', 'printsched'])
async def print_schedule(context):
    """This function prints out the mood check-in schedule for the user in the format:
    days of the week at times of day."""
    author = context.author
    [days, times] = mood_schedule_retrieval(author)
    word_days = bool_days_to_word_days(days)
    await context.send(m_const.PRINT_SCHEDULE_OUTPUT % (str(word_days), str(times)))


@mood_bot.command(name='delete_day', help='Delete day(s) from mood check schedule.',
                  aliases=['del_day', 'delday', 'deleteday', '-day', 'del_days', 'delete_days',
                           'deldays', 'deletedays', '-days', 'day-', 'days-'])
async def delete_day(context, *day_inputs):
    """This function removes days from the mood check-in schedule as specified by the user."""
    author = context.author
    [mood_days, _] = mood_schedule_retrieval(author)
    day_inputs_lower = list(map(lambda x: x.lower(), day_inputs))
    for day_input_y in day_inputs_lower:
        day_mo = sched_const.DAY_REGEX.search(day_input_y)
        if day_mo is None:
            await day_format_error(context, day_input_y)
        else:
            if day_input_y == 'everyday':
                for j in range(7):
                    mood_days[j] = False
                break
            elif day_input_y == 'weekdays':
                for j in range(5):
                    mood_days[j] = False
            elif day_input_y == 'weekends':
                for k in range(5, 7):
                    mood_days[k] = False
            else:
                mood_days[sched_const.DAY_DICTIONARY[day_input_y]] = False
    mood_schedule_storage(author, 'days', mood_days)
    await context.send(m_const.NEW_SCHEDULE_MESSAGE % ('days', bool_days_to_word_days(mood_days)))


@mood_bot.command(name='delete_time', help="Delete time(s) from mood check schedule. "
                                           "Enter 'all' to clear all the times from the schedule.",
                  aliases=['del_time', 'deltime', 'deletetime', '-time', 'time_del', 'time_delete',
                           'timedel', 'timedelete', 'delete_times', 'del_times', 'deletetimes', 'deltimes', '-times',
                           'time-', 'times-'])
async def delete_time(context, *time_inputs):
    """This function removes times from the mood check-in schedule as specified by the user."""
    author = context.author
    [_, mood_times] = mood_schedule_retrieval(author)
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
    mood_schedule_storage(author, 'times', mood_times)
    await context.send(m_const.NEW_SCHEDULE_MESSAGE % ('times', mood_times))


def mood_time_retriever(author):
    """This function takes the mood schedule and figures out when the next mood check will be."""
    [mood_days, mood_times] = mood_schedule_retrieval(author)
    if mood_days == [False, False, False, False, False, False, False] or mood_times == []:
        next_datetime = 0
    else:
        now = datetime.datetime.now()
        """returns integer 0-6 representing Monday-Sunday for today"""
        now_day = next_moodcheck_day = datetime.datetime.now().weekday()
        now_time = next_moodcheck_time = datetime.datetime.now().strftime('%H:%M:%S')
        found_next_moodcheck_day = False
        next_moodcheck_date_is_set = False
        moodcheck_weekdays = []
        days_until_check = 0
        for i, day_x in enumerate(mood_days):
            if day_x:
                found_next_moodcheck_day = True
                moodcheck_weekdays.append(i)
                # makes a list of the weekdays that have mood checks in terms of integers 0-6
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


@mood_bot.command(name='next_check', help='Provides the date and time of the next mood check.',
                  aliases=['next', 'check_next'])
async def next_check(context):
    """This function allows the user to call the mood_time_retriever function to
    figure out when the next mood check will be."""
    author = context.author
    check_datetime = mood_time_retriever(author)
    if check_datetime == 0:
        await context.send(m_const.NO_CHECK_SCHEDULED_MESSAGE)
    elif not autochecker_on(author):
        await context.send(m_const.NO_CHECK_BC_AUTO_OFF_MESSAGE)
    else:
        await context.send(m_const.NEXT_CHECK_MESSAGE % (str(check_datetime)))


def autochecker_on(author):
    """Returns whether the mood autochecker is ON/OFF as boolean."""
    mood_filename = str(author) + "_moodfile"
    schedule = shelve.open(mood_filename)
    if not os.path.exists(mood_filename + ".dat") or 'autocheck' not in schedule:
        autocheck = False
        schedule['autocheck'] = autocheck
    else:
        autocheck = schedule['autocheck']
    schedule.close()
    return autocheck


def set_autochecker(author, autocheck):
    """Turns mood autochecker ON/OFF."""
    mood_filename = str(author) + "_moodfile"
    schedule = shelve.open(mood_filename)
    schedule['autocheck'] = autocheck
    schedule.close()


""" MOOD CHECK FUNCTIONS """


@mood_bot.command(name='auto', help='Turns auto mood check ON/OFF.',
                  aliases=['auto_check', 'autocheck', 'autochecker', 'auto_checker'])
async def mood_auto_checker_switch(context, on_or_off):
    """This function waits until the next mood check is scheduled and then activates the mood check function."""
    author = context.author
    on_or_off = on_or_off.upper()
    if on_or_off == 'OFF':
        set_autochecker(author, False)
    elif on_or_off == 'ON':
        set_autochecker(author, True)
    else:
        await auto_checker_error(context, on_or_off)


@mood_bot.event
async def auto_check_nick():
    """Just testing the auto-mood-check on my own user id
    Doesn't seem like this function is being called at all."""
    target_time = mood_time_retriever(nick_username)
    if isinstance(target_time, datetime.datetime):
        while datetime.datetime.now() < target_time:
            if not autochecker_on(nick_username):
                break
            await asyncio.sleep(1)
            target_time = mood_time_retriever(nick_username)
        if autochecker_on(nick_username):
            await mood_reset(nick_username, False)
            await mood_check(nick_username, False)


@mood_bot.command(name='status', help='Reports whether mood auto checker is on or off, '
                                      'whether a mood check is in progress, '
                                      'and what stage of the mood check process is open if applicable.')
async def mood_status(context):
    author = context.author
    auto_checker_status = m_const.AUTO_CHECKER_OFF_MESSAGE
    if autochecker_on(author):
        auto_checker_status = m_const.AUTO_CHECKER_ON_MESSAGE
    await context.send(auto_checker_status)
    mood_check_status = m_const.MOOD_CHECK_NO_START_MESSAGE
    stage = current_stage(author)
    if stage > 0:
        mood_check_status = m_const.MOOD_CHECK_IN_PROGRESS_MESSAGE % stage_array[stage]
    await context.send(mood_check_status)


def mood_stamp_maker(author):
    mood_stamp = mood_diary_retrieval(author, 'type', 'last_entry')
    return mood_stamp


def rating_stamp_maker(author):
    rating_stamp = mood_diary_retrieval(author, 'rating', 'last_entry')
    return rating_stamp


def current_stage(author):
    mood_filename = str(author) + "_moodfile"
    diary = shelve.open(mood_filename)
    if not os.path.exists(mood_filename + ".dat") or 'stage' not in diary:
        stage = 0
        diary['stage'] = stage
    else:
        stage = diary['stage']
    diary.close()
    return stage


def open_next_stage(author, stage):
    mood_filename = str(author) + "_moodfile"
    diary = shelve.open(mood_filename)
    stage = (stage + 1) % 4
    diary['stage'] = stage
    diary.close()


def set_stage(author, desired_stage):
    mood_filename = str(author) + "_moodfile"
    diary = shelve.open(mood_filename)
    diary['stage'] = desired_stage
    diary.close()


@mood_bot.command(name='check', help='Run a mood check.')
async def mood_check(context, manual=True):
    """This function starts a mood check by recording current time and date and asking the user how they feel."""
    if manual:
        author = context.author
    else:
        author = context
    stage = current_stage(author)
    if stage == 0:
        entry_time = datetime.datetime.now()
        mood_diary_storage(author, 'date', entry_time.strftime('%Y/%m/%d %H:%M:%S'))
        await context.send(m_const.MOOD_CHECK_QUESTION % str(author))
        open_next_stage(author, stage)
    else:
        """If the date_gate isn't open, it checks to see which gate is open.
        This means that another mood check was in progress and is unfinished."""
        await time_stamp_message(context, author)
        if stage == 1:
            await context.send(m_const.MOOD_TYPE_LEFT_OFF_MESSAGE)
        else:
            mood_stamp = mood_stamp_maker(author)
            if stage == 2:
                await context.send(m_const.MOOD_RATING_LEFT_OFF_MESSAGE % mood_stamp)
            elif stage == 3:
                rating_stamp = rating_stamp_maker(author)
                await context.send(m_const.MOOD_WHY_LEFT_OFF_MESSAGE % (mood_stamp, rating_stamp))


@mood_bot.command(name='type', help='Report your mood.')
async def mood_type_selection(context, mood_type):
    """Allows the user to answer the mood_check function with their mood selection.
    And asks the user to rate their mood from 1 to 10."""
    author = context.author
    stage = current_stage(author)
    mood_type = mood_type.lower()
    if stage == 1:
        if mood_type not in m_const.MOOD_CHOICES:
            await mood_type_error(context, mood_type)
        else:
            mood_diary_storage(author, 'type', mood_type)
            await context.send(m_const.MOOD_RATING_QUESTION % mood_type)
            open_next_stage(author, stage)
    else:
        """If the type_gate isn't open, then a mood check is either not started or is in progress.
        Checks to see which gate is open."""
        if stage == 0:
            await context.send(m_const.START_MOOD_CHECK_ERROR_MESSAGE)
        else:
            await time_stamp_message(context, author)
            mood_stamp = mood_stamp_maker(author)
            if stage == 2:
                await context.send(m_const.MOOD_RATING_LEFT_OFF_MESSAGE % mood_stamp)
            elif stage == 3:
                rating_stamp = rating_stamp_maker(author)
                await context.send(m_const.MOOD_WHY_LEFT_OFF_MESSAGE % (mood_stamp, rating_stamp))


@mood_bot.command(name='rating', help='Rate your mood from 1 to 10.')
async def mood_rating_selection(context, mood_rating):
    """Allows user to enter their mood rating. Then, asks user to explain why they feel that way."""
    author = context.author
    stage = current_stage(author)
    if stage == 2:
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
            await context.send(m_const.MOOD_EXPLANATION_QUESTION % (author, qualifier, mood_type))
            open_next_stage(author, stage)
    else:
        """If the rating_gate isn't open, then either a mood check wasn't started properly or is still in progress.
        Checks to see which gate is open."""
        if stage == 0:
            await context.send(m_const.START_MOOD_CHECK_ERROR_MESSAGE)
        else:
            await time_stamp_message(context, author)
            if stage == 1:
                await context.send(m_const.MOOD_TYPE_LEFT_OFF_MESSAGE)
            elif stage == 3:
                mood_stamp = mood_stamp_maker(author)
                rating_stamp = rating_stamp_maker(author)
                await context.send(m_const.MOOD_WHY_LEFT_OFF_MESSAGE % (mood_stamp, rating_stamp))


@mood_bot.command(name='why', help='Explain why you are feeling the mood that you reported.',
                  aliases=['explanation', 'explan', 'explain', 'journal', 'y'])
async def mood_explanation(context, *why):
    """Allows the user to explain the reason behind their mood.
    Then, it tells the user that their mood entry has been saved (though, the data does get saved at each step.)
    The function then resets the gates so that another mood check can be started."""
    author = context.author
    stage = current_stage(author)
    if stage == 3:
        why = ' '.join(why)
        mood_diary_storage(author, 'why', why)
        await context.send(m_const.MOOD_CHECK_COMPLETE_MESSAGE)
        open_next_stage(author, stage)
    else:
        """If the why_gate is closed, then a mood check hasn't been started or is still in progress.
        Checks to see which mood gate is open."""
        if stage == 0:
            await context.send(m_const.START_MOOD_CHECK_ERROR_MESSAGE)
        else:
            await time_stamp_message(context, author)
            if stage == 1:
                await context.send(m_const.MOOD_TYPE_LEFT_OFF_MESSAGE)
            elif stage == 2:
                mood_stamp = mood_stamp_maker(author)
                await context.send(m_const.MOOD_RATING_LEFT_OFF_MESSAGE % mood_stamp)


"""MOOD DIARY FUNCTIONS"""


def mood_diary_storage(author, cat, data):
    """This function stores data to the mood diary (in the mood file) under the appropriate category.
    Essentially, this is how mood check entries are stored."""
    mood_filename = str(author) + "_moodfile"
    diary = shelve.open(mood_filename)
    if str(cat) in diary:
        mood_data = diary[str(cat)]
    else:
        mood_data = []
    mood_data.append(data)
    diary[str(cat)] = mood_data
    diary.close()


def mood_diary_retrieval(author, cat, arg):
    """This function gets entries from the mood diary to be displayed to the user via another function."""
    mood_filename = str(author) + "_moodfile"
    diary = shelve.open(mood_filename)
    data_entries = diary[str(cat)]
    output = ''
    if arg == 'last_entry':
        last_entry = len(data_entries) - 1
        output = data_entries[last_entry]
    diary.close()
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
    mood_filename = str(author) + '_moodfile'
    diary = shelve.open(mood_filename)
    if 'date' not in diary:
        context.send(m_const.DIARY_EMPTY_MESSAGE)
    else:
        date_data = diary['date']
        number_of_entries = len(date_data)
        if number_of_entries == 0:
            await context.send(m_const.DIARY_EMPTY_MESSAGE)
        elif number_of_entries == 1:
            await context.send(m_const.DIARY_COUNT_MESSAGE_SINGLE % (str(number_of_entries), str(date_data[0])))
        else:
            await context.send(m_const.DIARY_COUNT_MESSAGE_MULTIPLE
                               % (str(number_of_entries), str(date_data[0]), str(date_data[number_of_entries - 1])))
    diary.close()


@mood_bot.command(name='print_diary', help="Prints out entries from the mood diary. "
                                           "User specifies the start and end entries "
                                           "or specifies 'all' for all entries.",
                  aliases=['diary_print', 'printdiary', 'diaryprint'])
async def print_diary(context, start='all', end='0'):
    """Prints out the mood diary as specified by the user.
    User can either write 'all' for all entries, or can specify start and end entries."""
    author = context.author
    mood_filename = str(author) + '_moodfile'
    diary = shelve.open(mood_filename)
    if 'date' not in diary:
        await context.send(m_const.DIARY_EMPTY_MESSAGE)
    else:
        diary.close()  # so that we don't try opening the diary file twice, concurrently
        await mood_reset(context, False)  # makes sure that all the data is the same length
        diary = shelve.open(mood_filename)
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
                await context.send(' '.join(entry))
    diary.close()


@mood_bot.command(name='del_diary', help="Delete entries from the diary. User specifies the start and end entries, or "
                                         "specifies 'all' to delete all entries.",
                  aliases=['delete_diary', 'deletediary', 'diary_del', 'diarydel', 'diarydelete', 'diary_delete'])
async def delete_diary(context, start, end='0'):
    """User can remove entries from the mood diary, by specifying all entries or start and end entries."""
    author = context.author
    mood_filename = str(author) + '_moodfile'
    diary = shelve.open(mood_filename)
    if 'date' not in diary:
        await context.send(m_const.DIARY_EMPTY_MESSAGE)
    else:
        diary.close()  # so that we don't try opening the diary file twice, concurrently
        await mood_reset(context, False)  # makes sure that all the data is the same length
        diary = shelve.open(mood_filename)
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
            await context.send(m_const.DIARY_DELETE_COMPLETION_MESSAGE)
    diary.close()


@mood_bot.command(name='reset', help='Start over a mood check.')
async def mood_reset(context, manual=True):
    """Reset function: deletes any extra entries in the diary and re-initializes the stage variable."""
    if manual:
        author = context.author
    else:
        author = context
    mood_filename = str(author) + "_moodfile"
    diary = shelve.open(mood_filename)
    data_cats = [date_data, type_data, rating_data, why_data] = mass_diary_data_retrieval(diary)
    data_lengths = [len(date_data), len(type_data), len(rating_data), len(why_data)]
    if data_lengths[0] == data_lengths[1] == data_lengths[2] == data_lengths[3]:
        if manual:
            await context.send(m_const.NO_NEED_FOR_RESET_MESSAGE % str(author))
        diary.close()
    else:
        shortest_length = min(data_lengths)
        for cat in data_cats:
            while len(cat) > shortest_length:
                del cat[len(cat) - 1]
        mass_diary_data_storage(diary, date_data, type_data, rating_data, why_data)
        diary.close()
        set_stage(author, 0)
        if manual:
            await context.send(m_const.RESET_COMPLETE_MESSAGE % str(author))


mood_bot.run(MOOD_TOKEN)
