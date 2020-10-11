class MoodError(Exception):
    """Base class for other exceptions within the mood bot"""
    pass


class InputMoodError(MoodError):
    """Exception raised for errors in the input."""
    def __int__(self, *args):
        pass

    def __str__(self):
        if self.args[1] is None:
            return self.args[0]
        else:
            return f'{self.args[1]} -> {self.args[0]}'
