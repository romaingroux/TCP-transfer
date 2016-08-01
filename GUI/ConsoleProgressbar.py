import sys

class ConsoleProgressbar:
    """
    A class to draw a progress bar on stdout for time consumming processes.
    Code taken and adapted from http://stackoverflow.com/questions/3160699/python-progress-bar from user eusoubrasileiro
    """

    def __init__(self, repeat, prefix="", size=40):
        """
        Class constructor for a progress bar
        :param repeat:  an int, the number of repetition (time a process should be repeated) to fill the bar.
        :param prefix:  a str, a label to display on the left of the progress bar.
        :param size:    an int, the length (number of char long) of the progress bar.
        :return:        None
        """
        self.__step = repeat
        self.__prefix = prefix
        self.__size = size
        self.__current = 0

    def __show(self):
        x = int(self.__size * self.__current / self.__step)
        sys.stdout.write("%s [%s%s] %i/%i\r" % (self.__prefix, "="*x, " "*(self.__size-x), self.__current, self.__step))
        sys.stdout.flush()

    def update(self):
        """
        Call this method to update the progress bar by a step (the process of interest has proceed by a step).
        :return:       None
        """
        self.__show()
        if self.__current < self.__step:
            self.__current += 1
        else:
            pass
            sys.stdout.write("\n")
            # sys.stdout.flush()
