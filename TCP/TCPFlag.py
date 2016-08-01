
class TCPFlag:
    """
    A class containing static methods to construct special flags to be sent by TCPClient to TCPListener to instuct
    TCPListener of file names, file types and of a proper end of transmission. This class also contains static methods
    to check the presence of a flag in strings.
    Flags can be constructed for :
        file names :            a flag should have the following structure : FILENAMESTART<name>FILENAMEEND
        file types :            a flag should have the following structure : FILETYPESTART<type>FILETYPEEND where
                                <type> should be "serie", "movie" or "misc". "misc" is a default value to be used when
                                no special behaviour is required.
        end of transmission :   this flag is simply ENDTRANSMISSION
    """
    # to specify a file through a TCP connection
    FILENAMESTART = "FILENAMESTART"
    FILENAMEEND = "FILENAMEEND"

    # to specify a file type through a TCP connection
    FILETYPESTART = "FILETYPESTART"
    FILETYPEEND = "FILETYPEEND"

    # types of files
    TYPESERIE = "serie"
    TYPEMOVIE = "movie"
    TYPEMISC = "misc"

    # to specify a proper end of the transmission
    ENDTRANSMISSION = "ENDTRANSMISSION"

    def __init__(self):
        pass

    @staticmethod
    def build_filename_flag(name):
        """
        Given a name, build a filename flag.
        :param name:    a str, the name to include in the flag
        :return:        a str, the flag
        """
        return "%s%s%s" % (TCPFlag.FILENAMESTART, name, TCPFlag.FILENAMEEND)

    @staticmethod
    def build_serietype_flag():
        """
        Build a serie file type flag.
        :return:        a str, the flag
        """
        return "%s%s%s" % (TCPFlag.FILETYPESTART, TCPFlag.TYPESERIE, TCPFlag.FILETYPEEND)

    @staticmethod
    def build_movietype_flag():
        """
        Build a movie file type flag.
        :return:        a str, the flag
        """
        return "%s%s%s" % (TCPFlag.FILETYPESTART, TCPFlag.TYPEMOVIE, TCPFlag.FILETYPEEND)

    @staticmethod
    def build_misctype_flag():
        """
        Build a misc file type flag.
        :return:        a str, the flag
        """
        return "%s%s%s" % (TCPFlag.FILETYPESTART, TCPFlag.TYPEMISC, TCPFlag.FILETYPEEND)

    @staticmethod
    def build_endtransmission_flag():
        """
        Build a end of transmission flag.
        :return:        a str, the flag
        """
        return TCPFlag.ENDTRANSMISSION

    @staticmethod
    def check_filename_flag(string):
        """
        Given a string, checks the presence of a filename flag inside and returns the filename if there is a flag, None
        otherwise.
        :param string:      a str, the string to inspect
        :return:            a tupple of 4 elements, a boolean indicating whether a flag has has been found, a str
                            indicating the file name and the substring AFTER the end of the flag.
        """
        flag_start = string.find(TCPFlag.FILENAMESTART)
        flag_end = string.find(TCPFlag.FILENAMEEND) + len(TCPFlag.FILENAMEEND)
        name_start = -1
        name_end = -1

        if flag_start >= 0:
            name_start = flag_start + len(TCPFlag.FILENAMESTART)
            name_end = flag_end - len(TCPFlag.FILENAMEEND)

        # both tags have been found, this is a flag
        if (flag_start >= 0) and (flag_end >= 0):
            return True, string[name_start:name_end], string[flag_end:]
        # this is not a flag
        else:
            return False, "", string

    @staticmethod
    def check_filetype_flag(string):
        """
        Given a string, checks whether it contains a filetype flag.
        :param string:      a str, the string to inspect
        :return:            a tupple of 3 elements, a boolean indicating whether a flag has has been found, a str
                            indicating the file type and the substring AFTER the end of the flag.
        """

        flag_start = string.find(TCPFlag.FILETYPESTART)
        flag_end = string.find(TCPFlag.FILETYPEEND) + len(TCPFlag.FILETYPEEND)

        type_start = -1
        type_end = -1

        if flag_start >= 0:
            type_start = flag_start + len(TCPFlag.FILETYPESTART)
            type_end = flag_end - len(TCPFlag.FILETYPEEND)

        # both tags have been found, this is a flag
        if (flag_start >= 0) and (flag_end >= 0):
            return True, string[type_start:type_end], string[flag_end:]
        # this is not a flag
        else:
            return False, "", string

    @staticmethod
    def check_endtransmission_flag(string):
        """
        Given a string, checks whether it contains a ENDTRANSMITION flag.
        :param string:      a str, the string to inspect
        :return:            a tupple of 2 elements, a boolean indicating whether the flag has been found and a str
                            containing the substring coming BEFORE the flag.
        """

        flag_start = string.find(TCPFlag.ENDTRANSMISSION)

        if flag_start >= 0:
            return True, string[0:flag_start]
        else:
            return False, string
