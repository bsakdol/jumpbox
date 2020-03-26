import curses
import subprocess

from jumpbox import MenuItem
from jumpbox import clear_terminal
from netbox_api import NetboxAPI
from submenu_item import SubmenuItem


class NetboxItem(MenuItem):
    """A base class for menu options populated via Netbox.

    Arguments:
        text (str): The text to be displayed as the menu option.
        text_id (str): The unique ID string associated with the `text`.
        menu: The menu the option belongs to.
        should_exit (bool, optional): True if the menu should exit,
            False otherwise.
    """

    def __init__(self, text, text_id, menu=None, should_exit=False):
        super(NetboxItem, self).__init__(
            text=text, menu=menu, should_exit=should_exit)

        self.text_id = text_id

    def show(self, index):
        """Display the menu option.

        Returns:
            The format of the menu option::

                1 - Option 1: ID 1
                2 - Option 2: ID 2
        """
        return "%d - %s: %s" % (index + 1, self.text, self.text_id)


class DeviceItem(NetboxItem):
    """A menu option that is a network device.

    These options establish an SSH session to the option (device) that is
    selected from the menu.

    Arguments:
        text (str): The text to be displayed as the menu option.
        text_id (str): The unique ID string associated with the `text`.
        menu: The menu the option belongs to.
        should_exit (bool, optional): True if the menu should exit,
            False otherwise.
    """

    def __init__(self, text, text_id, menu=None, should_exit=False):
        super(DeviceItem, self).__init__(
            text=text, text_id=text_id, menu=menu, should_exit=should_exit)

    def set_up(self):
        """Setup to be performed before the action.

        Save the state of the current screen, then clear it from the terminal.
        """
        curses.def_prog_mode()
        clear_terminal()
        self.menu.clear_screen()

    def action(self):
        """Action to be performed when the option is selected.

        Estbalish an SSH session to the selected device.

        Raises:
            AttributeError: Call `commandline` via subprocess.
        """
        username = raw_input("Username: ")
        ssh = "ssh"
        commandline = "{0} {1} {2} {3}".format(ssh, "-l", "".join(username),
                                               "".join(self.text_id))
        try:
            completed_process = subprocess.run(commandline, shell=True)
            self.exit_status = completed_process.returncode
        except AttributeError:
            self.exit_status = subprocess.call(commandline, shell=True)

    def clean_up(self):
        """Cleanup to be performed after the action.

        Clear the screen, then return the parent menu to the screen in the
        previously saved state.
        """
        self.menu.clear_screen()
        curses.reset_prog_mode()
        curses.curs_set(1)  # reset doesn't do this properly
        curses.curs_set(0)


class SitesItem(NetboxItem):
    """A menu option that is a site.

    Sites menu options open a submenu upon selection.

    Arguments:
        text (str): The text to be displayed as the menu option.
        text_id (str): The unique ID string associated with the `text`.
        submenu: The submenu to be called when the option is selected.
        menu: The menu the option belongs to.
        should_exit (bool, optional): True if the menu should exit,
            False otherwise.
    """

    def __init__(self, text, text_id, submenu, menu=None, should_exit=False):
        super(SitesItem, self).__init__(
            text=text, text_id=text_id, menu=menu, should_exit=should_exit)

        self.text_id = text_id
        self.submenu = submenu
        if menu:
            self.submenu.parent = menu

    def set_menu(self, menu):
        """Set the menu the option belongs to.

        Arguments:
            menu: The menu the option belongs to.
        """
        self.menu = menu
        self.submenu.parent = menu

    def set_up(self):
        """Setup to be performed before the action.

        Save the state of the current screen, then clear it from the terminal.
        """
        curses.def_prog_mode()
        self.menu.clear_screen()

    def action(self):
        """Action to be performed when the option is selected.

        Start the submenu and display it on the screen.
        """
        self.submenu.start()

    def clean_up(self):
        """Cleanup to be performed after the action.

        Clear the screen, then return the parent menu to the screen in the
        previously saved state.
        """
        self.menu.clear_screen()
        curses.reset_prog_mode()
        curses.curs_set(1)  # reset doesn't do this properly
        curses.curs_set(0)

    def get_return(self):
        """Return the value of the selected option.

        Returns:
            :obj:`item`
        """
        return self.submenu.returned_value


class SearchItem(SubmenuItem):
    """A class to search devices.

    Search strings will only match on device hostnames.
    """

    def __init__(self, text, submenu=None, menu=None, should_exit=False):
        super(SearchItem, self).__init__(
            text=text, submenu=submenu, menu=menu, should_exit=should_exit)

        self.submenu = submenu
        if self.menu:
            self.submenu.parent = self.menu

        self.search_str = None

    def set_menu(self, menu):
        """Set the menu the option belongs to.

        Arguments:
            menu: The menu the option belongs to.
        """
        self.menu = menu
        self.submenu.parent = menu

    def set_up(self):
        """Setup to be performed before the action.

        Save the state of the current screen, then clear it from the terminal.
        """
        curses.def_prog_mode()
        clear_terminal()
        self.menu.clear_screen()

    def action(self):
        """Action to be performed when the option is selected.

        Search device hostnames for a full or partial string match, then
        launch the submenu with the results.
        """
        self.search_str = raw_input("Search: ")
        self.submenu.reset_menu()

        api = NetboxAPI()
        get_devices = api.get_devices(q=self.search_str)
        if len(get_devices) > 0:
            for index, item in enumerate(get_devices):
                text = item['display_name']
                text_id = item['primary_ip']['address']
                self.submenu.append_item(DeviceItem(text, text_id))

            clear_terminal()
            self.menu.clear_screen()
            curses.reset_prog_mode()
            curses.curs_set(1)  # reset doesn't do this properly
            curses.curs_set(0)

            self.submenu.start()

    def clean_up(self):
        """Cleanup to be performed after the action.

        Clear the screen, then return the parent menu to the screen in the
        previously saved state.
        """
        self.menu.clear_screen()
        curses.reset_prog_mode()
        curses.curs_set(1)  # reset doesn't do this properly
        curses.curs_set(0)

    def get_return(self):
        """Return the value of the selected option.

        Returns:
            :obj:`item`
        """
        return self.submenu.returned_value
