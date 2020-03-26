import curses
import subprocess

from jumpbox import MenuItem
from jumpbox import clear_terminal


class ExternalItem(MenuItem):
    """A base class for items to do stuff in the terminal, outside the menu.

    Arguments:
        text (str): The text to be displayed as the menu option.
        menu: The menu the option belongs to.
        should_exit (bool, optional): True if the menu should exit,
            False otherwise.
    """

    def __init__(self, text, menu=None, should_exit=False):
        super(ExternalItem, self).__init__(
            text=text, menu=menu, should_exit=should_exit)

    def set_up(self):
        """Setup to be performed before the action.

        Save the state of the current screen, then clear it from the terminal.
        """
        curses.def_prog_mode()
        clear_terminal()
        self.menu.clear_screen()

    def clean_up(self):
        """Cleanup to be performed after the action.

        Clear the screen, then return the parent menu to the screen in the
        previously saved state.
        """
        self.menu.clear_screen()
        curses.reset_prog_mode()
        curses.curs_set(1)  # reset doesn't do this properly
        curses.curs_set(0)


class QuickConnect(ExternalItem):
    """A menu item to establish an SSH session to a non-menu device.

    The user will manually input an IP address or hostname to establish the
    SSH session to.

    Arguments:
        text (str): The text to be displayed as the menu option.
        args:
        menu: The menu the option belongs to.
        should_exit (bool, optional): True if the menu should exit,
            False otherwise.

    """

    def __init__(self, text, args=None, menu=None, should_exit=False):
        super(QuickConnect, self).__init__(
            text=text, menu=menu, should_exit=should_exit)

        if args:
            self.args = args
        else:
            self.args = list()

        self.exit_status = None

    def action(self):
        """Action to be performed when the option is selected.

        Estbalish an SSH session to specified IP address or hostname.

        Raises:
            AttributeError: Call `commandline` via subprocess.
        """
        hostname = raw_input("Hostname/IP Address: ")
        username = raw_input("Username: ")
        ssh = "ssh"
        commandline = "{0} {1} {2} {3}".format(ssh, "-l", "".join(username),
                                               "".join(hostname))
        try:
            completed_process = subprocess.run(commandline, shell=True)
            self.exit_status = completed_process.returncode
        except AttributeError:
            self.exit_status = subprocess.call(commandline, shell=True)
