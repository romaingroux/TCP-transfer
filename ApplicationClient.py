# -*- coding: utf-8 -*-

import Tkinter as Tk
import ttk
import tkMessageBox as tkMB
import tkFileDialog as tkFD
import TCP_connection.TCPClient
import TCP_connection.TCPClientException
import GUI.SettingsPanel as SettingsPanel
import TCP_connection.TCPFlag as Tf
import optparse
import os
import ConfigParser


class ApplicationClient(Tk.Tk):

    # some parameters
    # size of the data chunk sent to the server
    BUFFSIZE = 4096

    def __init__(self, host, port, debug, *args, **kwargs):

        # initialize the main window
        Tk.Tk.__init__(self, *args, **kwargs)

        self.flag_debug = debug

        # file to send data
        self.file_path_default = "Please select a file to transfer"
        self.file_path = self.file_path_default
        self.file_type_default = Tk.StringVar()
        self.file_type = Tk.StringVar()
        self.file_type.set(self.file_type_default.get())

        # TCPClient
        self.host = host
        self.port = port
        self.tcpclient = TCP_connection.TCPClient.TCPClient(self.host, self.port, debug=self.flag_debug)

        # built interface
        # dimensions and parameters
        self.main_h = 270
        self.main_w = 700
        self.frame_w = self.main_w - 20
        self.frame_top_h = ((self.main_h - 50) / 5) * 1
        self.frame_mid_h = ((self.main_h - 50) / 5) * 3
        self.frame_bot_h = ((self.main_h - 50) / 5) * 1
        self.frame_padx = 10
        self.frame_pady = 10
        self.frame_bwd = 2
        self.mid1_col0_w = (self.frame_w / 5) * 4
        self.mid1_col1_w = (self.frame_w / 5) * 1
        self.but_w = 5
        self.progressbar_len = 400
        # other windows
        self.toplevel_settings = None
        # frames
        self.frame_top = None
        self.frame_mid = None
        self.frame_bot = None
        self.frame_radio = None
        # buttons
        self.browse_but = None
        self.submit_but = None
        self.quit_but = None
        # menus
        self.menubar = None
        self.file_menu = None
        self.help_menu = None
        # other widgets
        self.label = None
        self.progressbar = None
        self.radio_button = None
        self.logo = None
        self.canvas_logo = None

        self.construct_interface()

    def construct_interface(self):
        """
        Construct the main window interface.
        :return:    None
        """
        # initialize the main window
        self.title("RaspberryPi TCP Client")
        self['bg'] = "white"
        # set dimensions to be constant
        self.minsize(height=self.main_h, width=self.main_w)
        self.maxsize(height=self.main_h, width=self.main_w)
        self.resizable(height=False, width=False)

        # create menus
        # file menu
        self.menubar = Tk.Menu(self)
        self.file_menu = Tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Settings", command=self.listen_setting_menu)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Quit", command=self.close_app)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.config(menu=self.menubar)
        # help menu
        self.help_menu = Tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="Help", command=None)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        # main window is separated into three frames
        # --------------------------------------------------------------------------------------------------------------
        # top frame is a 1x8 gride, containing 8 time the RaspberryPi logo
        self.frame_top = Tk.Frame(self, width=self.frame_w, height=self.frame_bot_h, borderwidth=0,
                                  pady=self.frame_pady, relief=Tk.GROOVE)
        self.frame_top["bg"] = "white"
        self.frame_top.pack(side=Tk.TOP)
        self.logo = Tk.PhotoImage(file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "RaspberryPi_logo.gif"))
        for i in range(8):
            self.frame_top.columnconfigure(i, minsize=70)
            self.canvas_logo = Tk.Canvas(self.frame_top, width=60, height=75)
            self.canvas_logo["bg"] = "white"
            self.canvas_logo["borderwidth"] = 0
            self.canvas_logo["highlightthickness"] = 0
            self.canvas_logo.create_image(0, 0, image=self.logo, anchor=Tk.NW)
            self.canvas_logo.grid(row=0, column=i, sticky=Tk.NW)

        # --------------------------------------------------------------------------------------------------------------
        # midlle frame is a grid 3x2
        self.frame_mid = Tk.LabelFrame(self, width=self.frame_w, height=self.frame_mid_h, text="Selected file",
                                       borderwidth=self.frame_bwd, relief=Tk.GROOVE)
        self.frame_mid.grid_columnconfigure(0, minsize=self.mid1_col0_w)
        self.frame_mid.grid_columnconfigure(1, minsize=self.mid1_col1_w)
        self.frame_mid.pack(side=Tk.TOP, padx=self.frame_padx, pady=self.frame_pady)
        self.frame_mid.pack_propagate(0)
        # 1st row, path label, browse button and radio button for file type
        self.label = Tk.Label(self.frame_mid, text=self.file_path, anchor=Tk.W)
        self.label.config(width=60)
        self.label.grid(row=0, column=0, sticky=Tk.W)
        self.browse_but = Tk.Button(self.frame_mid, text="Browse", command=self.listen_browse_button, width=self.but_w)
        self.browse_but.grid(row=0, column=1)
        # 2nd row, progress bar and submit button
        self.progressbar = ttk.Progressbar(self.frame_mid, orient="horizontal", length=self.progressbar_len,
                                           mode="determinate")
        self.progressbar.grid(row=1, column=0, sticky=Tk.W)
        self.submit_but = Tk.Button(self.frame_mid, text="Submit", command=self.listen_submit_button, width=self.but_w)
        self.submit_but.grid(row=1, column=1)
        # 3rd row, a frame containing 3 radio buttons in a 1x3 grid
        self.frame_radio = Tk.Frame(self.frame_mid, width=self.frame_w, height=self.frame_mid_h/6)
        self.frame_radio.grid(row=2, column=0)
        button = Tk.Radiobutton(self.frame_radio, text="Movie", variable=self.file_type, value=Tf.TCPFlag.TYPEMOVIE,
                                command=self.listen_radio_button)
        button.grid(row=0, column=0)
        button = Tk.Radiobutton(self.frame_radio, text="Serie", variable=self.file_type, value=Tf.TCPFlag.TYPESERIE,
                                command=self.listen_radio_button)
        button.grid(row=0, column=1)
        button = Tk.Radiobutton(self.frame_radio, text="Misc", variable=self.file_type, value=Tf.TCPFlag.TYPEMISC,
                                command=self.listen_radio_button)
        button.grid(row=0, column=2)

        # --------------------------------------------------------------------------------------------------------------
        # bottom frame contains only quit button
        self.frame_bot = Tk.Frame(self, width=self.frame_w, height=self.frame_bot_h, borderwidth=self.frame_bwd,
                                  relief=Tk.GROOVE)
        self.frame_bot.pack(side=Tk.BOTTOM, padx=self.frame_padx, pady=self.frame_pady)
        self.frame_bot.pack_propagate(0)
        self.quit_but = Tk.Button(self.frame_bot, text="Quit", command=self.listen_quit_button, width=self.but_w)
        self.quit_but.pack(side=Tk.LEFT, padx=10)

    def get_file_size(self):
        """
        Open the file to be sent and compute the number of data chunks which will have to be sent to transfer to whole
        file according to the number of bytes sent at once (ApplicationClient.BUFFSIZE).
        :return:    an int, the number of chunks which will have to be sent.
        """
        with open(self.file_path, "rb") as f_data:
            start = f_data.tell()
            f_data.seek(0, 2)
            end = f_data.tell()
        return (end - start) // ApplicationClient.BUFFSIZE

    def send_data_routine(self, data):
        """
        Separated method to send the data. This allows this process to slow down otherwise the python main process
        overloads the CPU and the progress bar is not displayed properly.
        :param data:    a str, a data to be send through the TCPClient using TCPClient.send()
        :return:        None
        """

        self.tcpclient.send(data)
        self.progressbar.step(1)
        # force to update display
        self.progressbar.update()

    def debug(self, message):
        """
        Print the debug message if self.debug is True
        :param message: a str, the message to be displayed.
        :return: None
        """
        if self.flag_debug:
            print "%s %s" % ("ApplicationClient debug :", message)

    def reset(self):
        """
        Method resetting all relevant variable after sending a file for the next run.
        :return:    None
        """
        self.file_path = self.file_path_default
        self.file_type.set(self.file_type_default.get())
        self.label.configure(text=self.file_path)

    # methods for running and closing the application
    def run_app(self):
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.mainloop()

    def close_app(self):
        """
        Method called when quitting the program. Closed everything properly.
        :return:        None
        """
        self.tcpclient.close()
        self.debug("closing!")
        exit(0)

    # button listeners
    def listen_quit_button(self, *args):
        """
        Callback method to listen and respond to "Quit" button. When clicked, the close() method is called to close
        everything properly.
        :param args:    argument passed by the "Quit" button master
        :return:        None
        """
        # to use *args, otherwise code inspection sees it as unused
        len(args)
        self.debug("quit button pressed...")
        self.close_app()

    def listen_browse_button(self, *args):
        """
        Callback method to listen to "Browse" button. When clicked, it opens a file browser.
        :param args:    argument passed by the "Quit" button master
        :return:        None
        """
        # to use *args, otherwise code inspection sees it as unused
        len(args)
        self.debug("browse button pressed...")
        self.file_path = tkFD.askopenfilename(title="Choose a file to transfer", filetypes=[('avi files', '.avi'),
                                                                                            ('mp4 files', '.mp4')])
        self.label.configure(text=self.file_path)
        self.debug("file choosen : %s" % self.file_path)

    def listen_submit_button(self, *args):
        """
        Callback method to listen and respond to "Submit" button. When clicked, a TCP connection is opened and the file
        is sent. It also pops-up a window to display the progress of the data transfer.
        :param args:    argument passed by the "Submit" button master
        :return:        None
        """
        # to use *args, otherwise code inspection sees it as unused
        len(args)
        self.debug("submit button pressed...")

        # check that a file is selected
        if self.file_path == self.file_path_default:
            self.debug("no file selected...")
            tkMB.showerror("Error", "No file is selected.")
            self.reset()
            return

        # check that a file type is selected
        if self.file_type.get() == self.file_type_default.get():
            self.debug("no type selected...")
            tkMB.showerror("Error", "No file type is selected.")
            self.reset()
            return

        # set progress bar
        file_size = self.get_file_size()
        self.progressbar["value"] = 0
        self.progressbar["maximum"] = file_size

        # open connexion
        try:
            # open TCP connection
            self.tcpclient.connect()
        except TCP_connection.TCPClientException.TCPClientException as e:
            self.debug("exception caught during TCP connection opening!\n%s" % str(e.message))
            # close TCP connection
            self.tcpclient.close()
            # reset variables for next run
            self.reset()
            tkMB.showerror("Error", "TCP connection to host %s could not be established. Check your connection, the "
                                    "host address and that the host is listening on port %d." % (self.host, self.port))
            return

        # data transfer
        try:
            # open data file and send it
            with open(self.file_path, "rb") as f_data:
                # send a first chunk of data containing flags to instruct the server of the file name and type
                # the flags are constructed and read by DataFlag class
                # first chunk is : <FILENAMEFLAG><FILETYPEFLAG>
                chunk_data = ""
                if self.file_type.get() == Tf.TCPFlag.TYPEMISC:
                    chunk_data = Tf.TCPFlag.build_filename_flag(os.path.basename(self.file_path)) + \
                                 Tf.TCPFlag.build_misctype_flag()
                elif self.file_type.get() == Tf.TCPFlag.TYPEMOVIE:
                    chunk_data = Tf.TCPFlag.build_filename_flag(os.path.basename(self.file_path)) + \
                                 Tf.TCPFlag.build_movietype_flag()
                elif self.file_type.get() == Tf.TCPFlag.TYPESERIE:
                    chunk_data = Tf.TCPFlag.build_filename_flag(os.path.basename(self.file_path)) + \
                                 Tf.TCPFlag.build_serietype_flag()
                self.send_data_routine(chunk_data)
                # send the remaining of the data
                chunk_data = f_data.read(ApplicationClient.BUFFSIZE)
                while chunk_data:
                    self.send_data_routine(chunk_data)
                    chunk_data = f_data.read(ApplicationClient.BUFFSIZE)
                # send end of transmission flag
                chunk_data = Tf.TCPFlag.build_endtransmission_flag()
                self.send_data_routine(chunk_data)

        # data transfer has been interrupted, pop up an alert message box
        except TCP_connection.TCPClientException.TCPClientException as e:
            self.debug("exception caught during data transfer!\n%s" % str(e.message))
            # close TCP connection
            self.tcpclient.close()
            # reset variables for next run
            self.reset()
            tkMB.showerror("Error", "An error occurred during the data transfer. The file has not been transferred.")
            return
        # close TCP connection
        self.tcpclient.close()
        # reset variables for next run
        self.reset()
        # pop up a success message
        tkMB.showinfo(title="Data transfer done", message="Data have been successfully transferred to host : %s"
                                                          % str(self.host))

    def listen_radio_button(self, *args):
        """
        Callback method to listen to the radio button of the main window. When clicked, file_type is updated.
        :param args:    argument passed by the RadioButton master
        :return:        None
        """
        # to use *args, otherwise code inspection sees it as unused
        len(args)

        self.debug("radio button pressed...")
        self.debug("file type choosen : %s" % self.file_type.get())

    def listen_setting_menu(self, *args):
        len(args)
        self.debug("menu Settings button pressed...")
        self.toplevel_settings = SettingsPanel.SettingsPanel(master=self, debug=self.flag_debug, height=250, width=250)

if __name__ == "__main__":

    help_usage = "Usage: python ApplicationClient.py"
    help_epilog = "A TCP client to connect to a server running ApplicationServer.py. The program parameters are " \
                  "defined config/ApplicationServer.ini. There are 3 parameters. " \
                  "1) host : is an IP address to listen a connection from. Set it to 0.0.0.0 to allow connection " \
                  "from any client. 2) port : is the port which will be listened at for client connections. 3) debug " \
                  ": set the debugging verbosity ON or OFF."

    # parsing arguments
    parser = optparse.OptionParser(epilog=help_epilog, usage=help_usage)
    (options, args) = parser.parse_args()

    # parse configuration file
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(os.path.join(os.path.dirname(__file__), "config", "ApplicationClient.ini"))
    HOST = config_parser.get("connection", "host")
    PORT = config_parser.get("connection", "port")
    PORT = int(PORT)
    DEBUG = config_parser.get("verbosity", "debug")
    if DEBUG == "True":
        DEBUG = True
    else:
        DEBUG = False

    # run application
    App = ApplicationClient(host=HOST, port=PORT, debug=DEBUG)
    App.run_app()
