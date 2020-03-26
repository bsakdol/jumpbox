#!/usr/bin/env python

from external_item import QuickConnect
from jumpbox import *
from netbox_api import NetboxAPI
from netbox_item import *
from submenu_item import SubmenuItem


def main():
    """Initialize the menu.

    Everything needed to build the menu should be written within this function.
    """
    api = NetboxAPI()
    get_devices = api.get_devices()
    get_sites = api.get_sites()

    # Define the main menu
    main_menu = Jumpbox("Jumpbox Main", "Select an option...")

    # Search Hostnames option:
    # This is the `Search Hostnames` option to be displayed in the main menu.
    # Selecting this menu option will allow the user to input a string that
    # will return devices with hostnames matching (full or partial) the string.
    # Selecting an option from the filtered list of devices will establish an
    # SSH connection to the specified device.
    search_menu = Jumpbox("Search Results", "Select a device...")
    search_item = SearchItem("Search", submenu=search_menu, menu=main_menu)
    main_menu.append_item(search_item)

    # Sites option:
    # This is the `Sites` option to be displayed in the main menu. Selecting
    # this menu option will open the `Sites` submenu.
    sites_menu = Jumpbox("Devices by Site", "Select a site...")
    sites_item = SubmenuItem("Sites", submenu=sites_menu, menu=main_menu)
    main_menu.append_item(sites_item)

    # Sites submenu:
    # This is the `Sites` submenu that is displayed when the `Sites` option is
    # selected from the main menu. The options displayed in this submenu are
    # the sites configured in Netbox that have one or more devices assigned with
    # a primary IP address. Selecting an option from this submenu will open a
    # submenu of the devices associated with the selected site.
    for index, item in enumerate(get_sites):
        sites_submenu = Jumpbox(item['name'], "Select a device...")
        sites_submenu_item = SitesItem(
            item['name'],
            item['facility'],
            submenu=sites_submenu,
            menu=sites_menu)
        sites_menu.append_item(sites_submenu_item)
        # Devices by Site submenu:
        # This is the submenu that is displayed when a site is selected from
        # the `Sites` submenu. Selecting an option in this menu will establish
        # an SSH connection to the associated device.
        for index, item in enumerate(api.get_devices(item['slug'])):
            text = item['display_name']
            text_id = item['primary_ip']['address']
            sites_submenu.append_item(DeviceItem(text, text_id))

    # Quick Connect option:
    # This is the `Quick Connect` option to be displayed in the main menu.
    # Selecting this menu option will allow the user to input an IP address
    # or hostname and an SSH connection will be established to the specified
    # device.
    quick_connect = QuickConnect("Quick Connect")
    main_menu.append_item(quick_connect)

    # Devices option:
    # This is the `Devices` option to be displayed in the main menu. Selecting
    # of this menu option will open the `Devices` submenu.
    devices_menu = Jumpbox("All Devices", "Select a device...")
    devices_item = SubmenuItem(
        "All Devices", submenu=devices_menu, menu=main_menu)
    main_menu.append_item(devices_item)

    # Devices submenu:
    # This is the `Devices` submenu that is displayed when the `Devices` option
    # is selected from the main menu. There are no filters applied to this menu,
    # so all devices, in Netbox, with a primary IP address assigned will be
    # displayed in this submenu. Selecting an option in this menu will establish
    # an SSH connection to the associated device.
    for index, item in enumerate(get_devices):
        text = item['display_name']
        text_id = item['primary_ip']['address']
        devices_menu.append_item(DeviceItem(text, text_id))

    # Start the menu
    main_menu.start()


if __name__ == '__main__':
    main()
