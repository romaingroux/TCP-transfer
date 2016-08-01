import Tkinter as Tk


class SettingsPanel(Tk.Toplevel):

    def __init__(self, master, debug, *args, **kwargs):

        self.master = master
        self.flag_debug = debug

        Tk.Toplevel.__init__(self, master=master, *args, **kwargs)

        # variable for input fields
        self.host = Tk.StringVar()
        self.host.set(self.master.host)
        self.port = Tk.IntVar()
        self.port.set(self.master.port)
        # labels
        self.host_label = Tk.Label(self, text="Host :")
        self.host_label.grid(row=0, column=0)
        self.port_label = Tk.Label(self, text="Port :")
        self.port_label.grid(row=1, column=0)
        # input entry
        self.host_entry = Tk.Entry(self, textvariable=self.host, width=50)
        self.host_entry.grid(row=0, column=1)
        self.port_entry = Tk.Entry(self, textvariable=self.port, width=50)
        self.port_entry.grid(row=1, column=1)
        # these buttons are provided listeners from outside
        self.cancel_but = Tk.Button(self, text="Cancel", command=self.cancel_button_listener)
        self.cancel_but.grid(row=2, column=0)
        self.ok_but = Tk.Button(self, text="OK", command=self.ok_button_listener)
        self.ok_but.grid(row=2, column=1)

    def debug(self, message):
        """
        Print the debug message if self.debug is True
        :param message: a str, the message to be displayed.
        :return: None
        """
        if self.flag_debug:
            print "%s %s" % ("SettingsPanel debug :", message)

    # button listeners
    def ok_button_listener(self):
        self.debug("OK button pressed...")
        self.master.host = self.host.get()
        self.master.port = self.port.get()
        # update host and port in tcpclient
        self.master.tcpclient.set_host(self.master.host)
        self.master.tcpclient.set_port(self.master.port)
        self.debug("host has been changed to : %s" % self.host.get())
        self.debug("port has been changed to : %s" % self.port.get())
        self.close()

    def cancel_button_listener(self):
        self.debug("Cancel button pressed...")
        self.close()

    def close(self):
        self.debug("closing...")
        self.destroy()
