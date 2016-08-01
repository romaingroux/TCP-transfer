import socket
import TCPClientException


class TCPClient:
    """
    A class to send data through a TCP connection to a server. This class works together with TCPListener class being
    run on the server side.
    All exception caught trigger TCPClientException to be raised. If connect() method raises a TCPClientException, it
    means the connexion to the host could not be opened. If send() raises a TCPClientException, it means that an
    error occurred during the transfer.
    """

    BUFFERSIZE = 4096

    def __init__(self, host, port, debug=False):
        """
        Class constructor
        :param host:    a str, the host to connect to.
        :param port:    an int, the port to use for the remote connexion.
        :param debug:   a bool, whether or not to enable debug verbosity.
        :return:        None
        """
        self.__socket = socket.socket()
        self.__host = host
        self.__port = port
        self.__flag_connect = False
        self.__flag_debug = debug

    def set_port(self, port):
        """
        Set connecting port.
        :param port:    an int, the port to connect to host.
        :return:        None
        """
        self.__port = port

    def set_host(self, host):
        """
        Set connecting port.
        :param host:    a str, the host to connect to.
        :return:        None
        """
        self.__host = host

    def connect(self):
        """
        Connects to the host, on given port.
        :return:        None
        """
        # establishing connection
        try:
            self.__socket.connect((self.__host, self.__port))
            self.__flag_connect = True
            self.debug("connection open...")
        except Exception as e:
            self.debug("connection failed...")
            self.close()
            self.__flag_connect = False
            raise TCPClientException.TCPClientException(e.message)

    def send(self, data):
        """
        Send a chunk of data to the host. Requires to be connected to the host.
        :param data:    a string of data to send.
        :return:        None
        """
        try:
            if self.__flag_connect:
                self.__socket.sendall(data)
        except Exception as e:
            self.debug("exception caught while sending data...")
            # raise an exception for higher levels
            raise TCPClientException.TCPClientException(e.message)

    def close(self):
        """
        Close the connection and reset self.__socket to a new socket object.
        :return:        None
        """
        if self.__flag_connect:
            self.__socket.close()
            self.debug("connection closed...")
            self.__socket = socket.socket()

    def debug(self, message):
        """
        Print the debug message if self.__debug is True
        :param message: a str, the message to be displayed.
        :return:        None
        """
        if self.__flag_debug:
            print "%s %s" % ("TCPClient debug :", message)
