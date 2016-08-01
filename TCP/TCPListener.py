import socket
import os
import TCPFlag as Tf
import TCPListenerException


class TCPListener:
    """
    A class to receive data through a TCP connection from a client. This class works together with TCPClient class being
    run on the client class.
    This class can be sent some instructions by the client. This is done by sending special sequence of data (flags) at
    the  really beginning of the connection. The flags construction and detection is handled by the DataFlag class.
    The client can send two types of flags. The first flag (filename flag) instructs this class  of the file name to
    use to write incoming data. The second flag (filetype flag) instructs this class about the type of file being
    transmitted. These flags are optional. In case the filename flag is missing, the data are written in a file named
    using the client IP address. In case the filetype flag is missing, the file type is set to DataFlag.MISC which is
    a default value.
    In case a transfer is interrupted before being completed, the incoming data are erased.
    """

    # size of the data chunk read
    BUFFSIZE = 4096

    def __init__(self, host, port, debug=False):
        """
        Class constructor
        :param host: a string, the client to allow connection from
        :param port: an int, the port to use
        :param debug: a boolean, whether to display debugging information
        :return: nothing
        """

        self.__flag_debug = debug
        self.__flag_transfer_now = False
        self.__flag_transmission_end = False
        # parameters to set listening
        self.__host = host
        self.__port = port
        # parameters for writting incoming data
        self.__file_name = None
        self.__file_file = None
        self.__file_type = None
        # sockets and client address
        self.__socket = socket.socket()
        self.__client_socket = None
        self.__client_address = None

    def listen(self, max_connections):
        """
        Start listening on the port for client connexion.
        This function never ends. The only way is through a Ctrl-C call which is intercepted by a try/except block to
        properly handle the situation.
        :param max_connections: an int, the maximum number of simultaneous connexion allowed
        :return: nothing
        """
        self.debug("connecting...")
        self.__socket.bind((self.__host, self.__port))
        self.__socket.listen(max_connections)
        self.debug("listening...")

        while True:

            try:
                # treats connection and data transfert
                details = self.listen_routine()
                if self.__flag_transmission_end:
                    self.debug("data of type %s have been written at %s" % (details[1], details[0]))
                    # reset everything for next connection
                    self.reset()

            except (KeyboardInterrupt, TCPListenerException.TCPListenerException, RuntimeError) as e:
                # treats ctrl-C interruption - the only way of escaping this infinite loop
                if type(e) == KeyboardInterrupt:
                    self.debug("exception caught : keyboard interruption...")
                    # exit the program
                    self.debug("stop listening...")
                    self.close()
                # treats unexpected interruption of connection
                elif type(e) == TCPListenerException.TCPListenerException:
                    self.debug("exception caught :  improper end of transmission from client side...")
                    self.debug("data transfer interrupted...")
                    # erase incoming truncated file and reset parameters
                    self.__file_file.close()
                    os.remove(self.__file_name)
                    self.debug("incomplete file erased...")
                    self.reset()
                    continue
                # treats any other type of exception
                elif type(e) == RuntimeError:
                    self.debug("exception caught :  unexpected type of interruption...\n%s" % e.message)
                    # erase incoming file if truncated and reset parameters
                    if not self.__flag_transmission_end:
                        self.__file_file.close()
                        os.remove(self.__file_name)
                        self.debug("incomplete file erased...")
                    self.reset()
                    continue

    def listen_routine(self):
        """
        Routine to be executed by self.listen()
        If an exception is raised and interrupts a data transfer, the incomplete file is deleted.
        :return:        a tupple of 3 elements containing a the bool indicating whether or not data have been received,
                        a str indicating the name of the file where data have been written in case the client sent
                        something and the type of file it was (as described in DataFlag) in case the client sent
                        something.
        """
        # default values in case of KeyboardInterrupt exception
        client_file = None

        try:
            # accepts connexion and transfer data
            self.__client_socket, self.__client_address = self.__socket.accept()
            if self.__client_socket:
                self.debug("connecting to client %s..." % str(self.__client_address))
                self.__flag_transfer_now = True
                client_file = self.__client_socket.makefile("rb")

                # read incoming data, if transmitted data contain flags, they should start at the first position of
                # the first chunk of data and be CONCATENATED if more than one flag.
                # The first flag is a file name flag, the second flag is a file type flag. The folowwing bytes are data
                # If there is no file name flag, the file is named using the client IP address and the socket id.
                # If there is no file type flag, it is assumed to be "misc", as defined in DataFlag.
                self.__file_file = None
                self.__file_name = None
                self.__file_type = None
                i = 0
                chunk_data = client_file.read(TCPListener.BUFFSIZE)
                while chunk_data:
                    # check the presence of flags in the first chunk
                    if i == 0:
                        self.debug("receiving data from %s..." % str(self.__client_address))
                        # check the presence of a tags
                        tupple_filenameflag = Tf.TCPFlag.check_filename_flag(chunk_data)
                        # remove filename flag
                        chunk_data = tupple_filenameflag[2]
                        tupple_filetypeflag = Tf.TCPFlag.check_filetype_flag(chunk_data)
                        # remove filetype flag
                        chunk_data = tupple_filetypeflag[2]
                        # file name flag
                        if tupple_filenameflag[0]:
                            self.__file_name = tupple_filenameflag[1]
                        else:
                            self.__file_name = "%s_%s.dat" % (str(self.__client_address[0]),
                                                              str(self.__client_address[1]))
                        # file type flag, by default it is TCPFlag.TYPEMISC
                        if tupple_filetypeflag[0]:
                            self.__file_type = tupple_filetypeflag[1]
                        else:
                            self.__file_type = Tf.TCPFlag.TYPEMISC
                        self.__file_file = open(self.__file_name, "wb")
                        self.__file_file.write(chunk_data)
                    else:
                        self.__file_file.write(chunk_data)
                    i += 1
                    chunk_data = client_file.read(TCPListener.BUFFSIZE)
                    # at the end of the last chunk of data a end of transmission flag should be present to indicate a
                    # proper end of transmission from the client side otherwise it indicates an improper end of
                    # transmission.
                    self.__flag_transmission_end, chunk_data = Tf.TCPFlag.check_endtransmission_flag(chunk_data)
                    if self.__flag_transmission_end:
                        # write was is coming before the flag
                        self.__file_file.write(chunk_data)
                        break
                # check that end of transmission flag has been found
                if not self.__flag_transmission_end:
                    raise TCPListenerException.TCPListenerException("Improper end of transmission on client side!")
                # close socket associated file
                if self.__flag_transmission_end:
                    self.__file_file.close()
                # close client connection
                self.__client_socket.close()
                self.debug("connection to client closed...")
                self.__flag_transfer_now = False

            file_name = self.__file_name
            file_type = self.__file_type
            return file_name, file_type

        # catch Ctrl-C to interrupt self.listen() or any other exception
        except (KeyboardInterrupt, TCPListenerException.TCPListenerException, Exception) as e:

            if self.__client_socket and client_file:
                client_file.close()

            if type(e) == KeyboardInterrupt:
                raise KeyboardInterrupt()
            elif type(e) == TCPListenerException.TCPListenerException:
                raise TCPListenerException.TCPListenerException()
            else:
                raise RuntimeError()

    def reset(self):
        """
        Reset parameters as their were at instanciation.
        :return:    None
        """
        self.debug("resetting...")
        # flag indicating the end of transmission
        self.__flag_transmission_end = False
        self.__flag_transfer_now = False
        # parameters for writing incoming data
        self.__file_name = None
        self.__file_file = None
        self.__file_type = None
        # sockets and client address
        self.__client_socket = None
        self.__client_address = None

        if self.__flag_debug:
                    print ""
                    print ""

    def close(self):
        """
        Method to call when stopping listening and closing the program, to handle everything properly.
        :return:    None
        """
        if self.__client_socket:
            self.__client_socket.close()
            self.debug("connection to client closed...")
        # a transfer has been interrupted, erase the incomplete file
        if self.__flag_transfer_now and (not self.__file_file.closed):
            self.debug("data transfer interrupted...")
            self.__file_file.close()
            os.remove(self.__file_name)
            self.debug("incomplete file erased...")
        self.__socket.close()
        self.debug("quitting...")
        exit(0)

    def debug(self, message):
        """
        Print the debug message if self.__debug is True
        :param message:
        :return:
        """
        if self.__flag_debug:
            print "%s %s" % ("TCPListener debug :", message)
