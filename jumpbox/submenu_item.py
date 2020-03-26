import curses

from jumpbox import MenuItem


class SubmenuItem(MenuItem):
    """A base class for menu items that open a submenu.

    Arguments:
        text (str): The text to be displayed as the menu option.
        submenu: The submenu to be called when the option is selected.
        menu: The menu the option belongs to.
        should_exit (bool, optional): True if the menu should exit,
            False otherwise.
    """

    def __init__(self, text, submenu, menu=None, should_exit=False):
        super(SubmenuItem, self).__init__(
            text=text, menu=menu, should_exit=should_exit)

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
