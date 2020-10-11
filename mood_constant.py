""" These are the preset choices for mood check-ins. """
MOOD_CHOICES = ('good', 'bad', 'okay', 'meh', 'happy', 'sad', 'angry', 'upset', 'depressed', 'hungry',
                'tired', 'bored', 'irritated', 'stressed', 'frustrated', 'ashamed', 'guilty', 'worried',
                'lonely', 'prideful', 'confused', 'disgusted', 'surprised', 'disappointed')

"""All String Messages for the mood_bot"""
DAY_FORMAT_ERROR_MESSAGE = "Please enter a valid day of the week or a term like 'Everyday' or 'Weekdays' or 'Weekends'."
TIME_DUPLICATE_ERROR_MESSAGE = 'Time is already in schedule.'
NEW_SCHEDULE_MESSAGE = 'The %s in your mood schedule are now:\n%s'
NO_TIME_ERROR_MESSAGE = "Sorry, that time is not in your mood check schedule. Please choose from the following: "
TIME_FORMAT_ERROR_MESSAGE = 'Please write time in HH:MM format.'
PRINT_SCHEDULE_OUTPUT = 'Your mood check schedule is %s at %s'
NO_CHECK_SCHEDULED_MESSAGE = 'There is no mood check scheduled.'
NO_CHECK_BC_AUTO_OFF_MESSAGE = 'There is no upcoming mood check because the auto mood checker is turned off.'
NEXT_CHECK_MESSAGE = 'Your next mood check will be at %s'
AUTO_CHECK_INPUT_ERROR_MESSAGE = 'Please specify whether the auto checker is ON or OFF.'
AUTO_CHECKER_OFF_MESSAGE = 'The auto mood checker is OFF.'
AUTO_CHECKER_ON_MESSAGE = 'The auto mood checker is ON.'
MOOD_CHECK_NO_START_MESSAGE = 'A mood check has not been started.'
MOOD_CHECK_IN_PROGRESS_MESSAGE = 'A mood check is in progress, and is currently in the mood %s stage.'
MOOD_CHECK_QUESTION = f"How are you feeling, %s?\n Please select from the following mood types:\n" \
                      f"{str(MOOD_CHOICES)}\nPlease respond by typing 'mood_type' followed by your selected mood."
MOOD_RATING_QUESTION = f"On a scale from 1 to 10, how %s do you feel?\n" \
                       f"Please respond by typing 'mood_rating' followed by the your selected integer."
MOOD_CHECK_COMPLETE_MESSAGE = 'Thank you. Your mood entry has been stored.'
MOOD_EXPLANATION_QUESTION = "%s, why do you feel %s %s?\n" \
                            "Please respond by typing 'mood_why' followed by your explanation."
UNFINISHED_MOOD_CHECK_MESSAGE = 'You have an unfinished mood check from %s.'
START_MOOD_CHECK_ERROR_MESSAGE = 'Please start a mood check first.'
MOOD_TYPE_ERROR_MESSAGE = f'Please enter in one of the following mood types:\n{str(MOOD_CHOICES)}'
MOOD_TYPE_LEFT_OFF_MESSAGE = 'You left off at the mood type.'
MOOD_RATING_LEFT_OFF_MESSAGE = 'You left off at rating. The mood type was %s.'
MOOD_WHY_LEFT_OFF_MESSAGE = 'You left off at the explanation. The mood type was %s and the rating was %s.'
RATING_ERROR_MESSAGE = 'Please enter an integer from 1 to 10.'
INTEGER_MESSAGE_FOR_DIARY = 'Please use integers to specify the start and end entries.'
DIARY_EMPTY_MESSAGE = 'Diary is empty. Please do a mood check to add an entry.'
DIARY_COUNT_MESSAGE_SINGLE = 'There is %s entry in the mood diary.\nThis entry was on %s.'
DIARY_COUNT_MESSAGE_MULTIPLE = 'There are %s entries in the mood diary.\n' \
                               'The first entry was on %s and the last entry was on %s'
OUT_OF_DIARY_RANGE_MESSAGE = 'For start and end entries, please specify integers from 1 to %s.'
DIARY_DELETE_COMPLETION_MESSAGE = 'Your specified entries have been successfully deleted.'
NO_NEED_FOR_RESET_MESSAGE = 'Mood checking does not need to be reset for %s.'
RESET_COMPLETE_MESSAGE = 'Mood checking has been reset for %s. You can now start a new mood check.'
