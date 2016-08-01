import TCP_connection.TCPListener
import optparse
import os
import ConfigParser

if __name__ == "__main__":

    help_usage = "Usage: python ApplicationServer.py"
    help_epilog = "A TCP listener to handle connections from client using ApplicationClient.py to send data. " \
                  "The program parameters are defined config/ApplicationServer.ini. There are 4 parameters. " \
                  "1) host : is an IP address to listen a connection from. Set it to 0.0.0.0 to allow " \
                  "connection from any client. 2) port : is the port which will be listened at for client connections" \
                  ". 3) : max_connection is the maximum number of clients which can connect at the same time. It is " \
                  "recommended to use 1. The program has not been written nor tested for higher values. 4) debug : " \
                  "set the debugging verbosity ON or OFF." \
                  "Finally, this program runs indefinitely and can only be interrupted by Ctrl-C. The data are " \
                  "written in a file which name is i) specified by the client or ii) constructed using the client " \
                  "address."

    # parsing arguments
    parser = optparse.OptionParser(epilog=help_epilog, usage=help_usage)
    (options, args) = parser.parse_args()

    # parse configuration file
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(os.path.join(os.path.dirname(__file__), "config", "ApplicationServer.ini"))
    HOST = config_parser.get("connection", "host")
    PORT = config_parser.get("connection", "port")
    PORT = int(PORT)
    MAX_CONN = config_parser.get("connection", "max_connections")
    MAX_CONN = int(MAX_CONN)
    if MAX_CONN <= 0:
        MAX_CONN = 1
    DEBUG = config_parser.get("verbosity", "debug")
    if DEBUG == "True":
        DEBUG = True
    else:
        DEBUG = False

    listener = TCP_connection.TCPListener.TCPListener(HOST, PORT, DEBUG)
    # enters an infinite loop which can only be escaped by Ctrl-C (this case is treated by an exception manager)
    listener.listen(MAX_CONN)
