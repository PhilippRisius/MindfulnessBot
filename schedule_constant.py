import re

DAYS_OF_WEEK = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

DAY_REGEX = re.compile(r'\b((mon|tues|wed(nes)?|thur(s)?|fri|sat(ur)?|sun)(day)?)|'
                       r'(everyday|weekend(s)?|weekday(s)?)\b', re.I)

DAY_DICTIONARY = {'monday': 0, 'mon': 0, 'tuesday': 1, 'tues': 1, 'tue': 1, 'wednesday': 2, 'wednes': 2, 'wed': 2,
                  'thursday': 3, 'thurs': 3, 'thur': 3, 'friday': 4, 'fri': 4, 'saturday': 5, 'satur': 5, 'sat': 5,
                  'sunday': 6, 'sun': 6}