import json
import re
import urllib2


class NetboxAPI(object):
    """Get data from Netbox.

    Use the Netbox API to gather the relevant information to be displayed in
    the menu system.

    Notes:
        If Netbox is not being used, this module should be deleted and replaced
        with a similar module to gather the relevant information. However, a
        similar format should be used in order to maintain the integrity of the
        menu system and display options.
    """

    def __init__(self):
        self.base_url = 'http://<netbox_url>/api/'

    def api_call(self, req):
        """GET a JSON response from the Netbox API.

        Arguments:
            req (str): The URL for the API request.

        Returns:
            The JSON response for the Netbox GET request.

        Raises:
            HTTPError: Prints the HTTP error code.
            URLError: Prints the reason for the URL error.
        """
        self.req = req
        try:
            request = urllib2.urlopen(self.req)
            response = json.load(request)
            return response
        except urllib2.HTTPError, err:
            return "HTTP Error: " + str(err.code)
        except urllib2.URLError, err:
            return "URL Error: " + str(err.reason)

    def get_devices(self, site_slug=None, q=None):
        """GET devices from Netbox.

        Arguments:
            site_slug (str, optional): The site slug associated with Sites in
                Netbox. Used to only GET devices associated with a particular
                site. Default is None.
            q (str, optional): A string to filter returned devices.

        Returns:
            The JSON data for the requested devices.

        Notes:
            The JSON data returned in this function has been cleaned by the
            `format_devices` method.
        """
        devices_url = 'dcim/devices/?limit=0&has_primary_ip=True'
        if site_slug:
            get_url = self.base_url + devices_url + '&site=' + site_slug
        elif q:
            get_url = self.base_url + devices_url + '&q=' + q
        else:
            get_url = self.base_url + devices_url

        response = self.api_call(get_url)
        return self.format_devices(response['results'])

    def get_sites(self):
        """GET sites from Netbox.

        Returns:
            The JSON data for the requested sites.

        Notes:
            The JSON data returned in this function has been cleaned by the
            `format_sites` method.
        """
        sites_url = 'dcim/sites/?limit=0'
        get_url = self.base_url + sites_url

        response = self.api_call(get_url)

        return self.format_sites(response['results'])

    def format_devices(self, data):
        """Format the device data returned from Netbox.

        Arguments:
            data: The JSON data returned by the API call to Netbox.

        Returns:
            The JSON `data` after the ```primary_ip``` has been cleaned of CIDR
            notation and the device hostname member number has been removed.
        """
        # This section removes the CIDR notation from the ```primary_ip``` field
        # of the JSON data. The JSON response also includes a ```primary_ip4`
        # field, which is left as-is.
        for index, item in enumerate(data):
            if re.search('[/]\d+$', item['primary_ip']['address']):
                item['primary_ip']['address'] = re.sub(
                    '[/]\d+$', '', item['primary_ip']['address'])

        # This section removes the device member number from the
        # ```display_name``` field of the JSON data. This is the field that
        # contains the hostname of the device.
        for index, item in enumerate(data):
            if re.search('-\d$', item['display_name']):
                item['display_name'] = re.sub('-\d$', '', item['display_name'])

        return data

    def format_sites(self, data):
        """Format the sites data returned from Netbox.

        This examines each individual site and determines if there are any
        devices, with a primary IP address, assigned to it. For sites that do
        not have a device, with a primary IP address, it is removed from the
        list of active sites.

        Returns:
            The list of sites with one or more devices, with a primary IP
            address, assigned.
        """
        for index, item in enumerate(data):
            if item['count_devices'] <= 0:
                data.pop(index)

        return data
