import curses
import os
import platform

from version import __version__


class Jumpbox(object):
    """A class that builds a menu and allows a user to interact with it.

    Build the menu based on items passed in from various item classes to
    ensure consistent formatting and behavior.

    Attributes:
        currently_active_menu: A variable to hold the currently active menu
            or None if no menu is active.
        stdscr: The Curses initialization variable.

    Arguments:
        screen: Curses window associated with the visible menu.
        highlight: Text color pair used for highlighting a menu option.
        normal: Text color pair used for menu options not highlited.
        term_y (int): The max Y coordinate of the terminal (height).
        term_x (int): The max X coordinate of the terminal (width).
        items: The list of options used to build the menu.
        current_option (int): The index of the highlighted menu option.
        selected_option (int): The index of the user selected menu option.
        returned_value: Value returned by the selected menu option.
        should_exit (bool): True if the menu should exit.
        parent: Parent menu of the current menu or None.
        previous_active_menu: Previously active menu or None.
        exit_item: The displayed menu option that allows the user to exit.
        _running (bool): True if the menu is actively running.
    """

    currently_active_menu = None
    stdscr = None

    def __init__(self, title=None, subtitle=None, show_exit_option=True):
        """
        Arguments:
            title (str): The title of the menu.
            subtitle (str): The subtitle of the menu.
            show_exit_option (bool): True if the exit option should be
                displayed.
        """
        self.title = title
        self.subtitle = subtitle
        self.show_exit_option = show_exit_option

        self.screen = None
        self.highlight = None
        self.normal = None

        self.term_y = 0
        self.term_x = 0

        self.items = list()
        self.current_option = 0
        self.selected_option = -1
        self.returned_value = None
        self.should_exit = False
        self.parent = None
        self.previous_active_menu = None

        self.exit_item = ExitItem(menu=self)

        self._running = False

    def __repr__(self):
        return "%s: %s. %d items" % (self.title, self.subtitle,
                                     len(self.items))

    @property
    def current_item(self):
        """The currently highlighted menu option.

        This is the menu option that is currently highlighted.

        Returns:
            MenuItem or None
        """
        if self.items:
            return self.items[self.current_option]
        else:
            return None

    @property
    def selected_item(self):
        """The selected menu item.

        This is the menu option that is selected by the user.

        Returns:
            MenuItem or None
        """
        if self.items and self.selected_option != -1:
            return self.items[self.current_option]
        else:
            return None

    def append_item(self, item):
        """Append a menu item to the menu options list.

        This will take a menu option and append it to the end of the menu list,
        before the exit option appears.

        Arguments:
            item (:obj:`str`): The menu option to be added to the `items` list.
        """
        did_remove = self.remove_exit()
        item.menu = self
        self.items.append(item)
        if did_remove:
            self.add_exit()
        if self.screen:
            self.term_y, self.term_x = self.screen.getmaxyx()
            if self.term_y < 6 + len(self.items):
                self.screen.resize(len(self.items) + 6, self.term_x)
            self.draw()

    def reset_menu(self):
        """Reset the menu to a blank list."""
        self.items = list()

    def add_exit(self):
        """Add the exit menu option.

        At the end of the menu options list, add an option that allows the user
        to signal the menu to exit.

        Returns:
            bool: True if the option needs to be added, False otherwise.
        """
        if self.items:
            if self.items[-1] is not self.exit_item:
                self.items.append(self.exit_item)
                return True
        return False

    def remove_exit(self):
        """Remove the exit menu option.

        If desireable, remove the exit menu option from the end of the items
        list. This is used to ensure there is not a duplicate exit menu option.

        Returns:
            bool: True if the option needs to be removed, False otherwise.
        """
        if self.items:
            if self.items[-1] is self.exit_item:
                del self.items[-1]
                return True
        return False

    def _wrap_start(self):
        """Create a wrapper to start the menu."""
        if self.parent is None:
            curses.wrapper(self._main_loop)
        else:
            self._main_loop(None)
        Jumpbox.currently_active_menu = None
        self.clear_screen()
        clear_terminal()
        Jumpbox.currently_active_menu = self.previous_active_menu

    def start(self, show_exit_option=None):
        """Start the menu and allow the user to interact with it.

        This is called from ```main``` and signals the menu to run. It should
        not be called more than one time.

        Arguments:
            show_exit_option (bool, optional): True if exit option should be
                displayed in the list, False otherwise. Default is True.
        """
        self.previous_active_menu = Jumpbox.currently_active_menu
        Jumpbox.currently_active_menu = None

        self.current_option = 0

        self.should_exit = False

        if show_exit_option is None:
            show_exit_option = self.show_exit_option

        if show_exit_option:
            self.add_exit()
        else:
            self.remove_exit()

        self._wrap_start()

    def _main_loop(self, scr):
        """Loop the menu, until the user signals to exit."""
        if scr is not None:
            Jumpbox.stdscr = scr
        self.term_y, self.term_x = Jumpbox.stdscr.getmaxyx()
        self.screen = curses.newpad(len(self.items) + 6, self.term_x)
        self._set_up_colors()
        curses.curs_set(0)
        Jumpbox.stdscr.refresh()
        self.draw()
        Jumpbox.currently_active_menu = self
        self._running = True
        while self._running is not False and not self.should_exit:
            self.process_user_input()

    def draw(self):
        """Draw the menu in the terminal.

        This should be called whenever something changes that needs to be
        refreshed on the screen.
        """
        self.screen.border(0)
        if self.title is not None:
            self.screen.addstr(2, 2, self.title, curses.A_UNDERLINE)
        if self.subtitle is not None:
            self.screen.addstr(4, 2, self.subtitle, curses.A_BOLD)

        for index, item in enumerate(self.items):
            if self.current_option == index:
                text_style = self.highlight
            else:
                text_style = self.normal
            self.screen.addstr(index + 5, 4, item.show(index), text_style)

        self.screen.addstr(index + 5, self.term_x - len(__version__) - 2,
                           __version__, curses.A_BOLD)

        self.term_y, self.term_x = Jumpbox.stdscr.getmaxyx()
        top_row = 0
        if len(self.items) + 6 > self.term_y:
            if self.term_y + self.current_option < len(self.items) + 6:
                top_row = self.current_option
            else:
                top_row = len(self.items) + 6 - self.term_y

        self.screen.refresh(top_row, 0, 0, 0, self.term_y - 1, self.term_x - 1)

    def get_input(self):
        """Wait for user input.

        Returns:
            int: Ordinal value of a single character.
        """
        return Jumpbox.stdscr.getch()

    def process_user_input(self):
        """Process the user input.

        After the user presses a single key, determine what to do with the
        key press.

        Returns:
            `get_input`
        """
        user_input = self.get_input()

        go_to_max = ord("9") if len(self.items) >= 9 else ord(
            str(len(self.items)))

        if ord('1') <= user_input <= go_to_max:
            self.go_to(user_input - ord('0') - 1)
        elif user_input == curses.KEY_DOWN:
            self.go_down()
        elif user_input == curses.KEY_UP:
            self.go_up()
        elif user_input == curses.KEY_RIGHT:
            self.select()
        elif user_input == curses.KEY_LEFT:
            self.current_option = len(self.items) - 1
            self.select()
        elif user_input == curses.KEY_RESIZE:
            self._running = False
            self._main_loop(None)
        elif user_input == ord("\n"):
            self.select()

        return user_input

    def go_to(self, option):
        """Go to the option entered by the user as a number.

        Arguments:
            option (int): The menu item to go to.
        """
        self.current_option = option
        self.draw()

    def go_down(self):
        """Go down one option.

        If the currently highlighted option is the last option in the list,
        wrap to the first menu option.
        """
        if self.current_option < len(self.items) - 1:
            self.current_option += 1
        else:
            self.current_option = 0
        self.draw()

    def go_up(self):
        """Go up one option.

        If the currently highlighted option is the first option in the list,
        wrap to the last menu option.
        """
        if self.current_option > 0:
            self.current_option += -1
        else:
            self.current_option = len(self.items) - 1
        self.draw()

    def select(self):
        """Select the current menu option.

        When the option is selected, it will run any associated actions.
        """
        self.selected_option = self.current_option
        self.selected_item.set_up()
        self.selected_item.action()
        self.selected_item.clean_up()
        self.returned_value = self.selected_item.get_return()
        self.should_exit = self.selected_item.should_exit

        if not self.should_exit:
            self.draw()

    def exit(self):
        """Signal the menu to exit."""
        self.should_exit = True

    def _set_up_colors(self):
        """Define the color pairs used for highlighting the menu options."""
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.highlight = curses.color_pair(1)
        self.normal = curses.A_NORMAL

    def clear_screen(self):
        """Clear the screen that belongs to the current menu."""
        self.screen.clear()
        Jumpbox.stdscr.erase()
        Jumpbox.stdscr.refresh()


class MenuItem(object):
    """A generic menu item.

    This is the base class for creating any options that will be displayed in
    the menu options list. This class shouldn't be directly referenced when
    adding menu options.

    Arguments:
        text (str): The text to be displayed as the option.
        menu (:obj:`item`, optional): The menu the option belongs to.
        should_exit (bool, optional): True if the menu should exit, False
            otherwise. Default is False.
    """

    def __init__(self, text, menu=None, should_exit=False):
        self.text = text
        self.menu = menu
        self.should_exit = should_exit
        self.should_exit = should_exit

    def __str__(self):
        return "%s %s" % (self.menu.title, self.text)

    def show(self, index):
        """Display the menu option.

        Returns:
            The format of the menu option::

                1 - Option 1
                2 - Option 2
        """
        return "%d - %s" % (index + 1, self.text)

    def set_up(self):
        """Setup to be performed before the action."""
        pass

    def action(self):
        """Action to be performed when the option is selected."""
        pass

    def clean_up(self):
        """Cleanup to be performed after the action."""
        pass

    def get_return(self):
        """Return the value of the selected option.

        Returns:
            :obj:`item`
        """
        return self.menu.returned_value


class ExitItem(MenuItem):
    """The exit option for the current menu.

    Arguments:
        text (str, optional): The text to be displayed for the option.
        menu (:obj:`item`, optional): The menu the item belongs to.
    """

    def __init__(self, text="Exit", menu=None):
        super(ExitItem, self).__init__(text=text, menu=menu, should_exit=True)

    def show(self, index):
        """Display the menu option.

        Arguments:
            index (int): Index of the menu option in the list.

        Returns:
            The format of the menu option::

                4 - Return to Locations menu
                OR
                4 - Exit
        """
        if self.menu and self.menu.parent:
            self.text = "Return to %s menu" % self.menu.parent.title
        else:
            self.text = "Exit"
        return super(ExitItem, self).show(index)


def clear_terminal():
    """Clear the terminal.

    Calls the platform specific command to reset the terminal and clear any
    residual commands.

    Examples:
        >>> reset
    """
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('reset')
