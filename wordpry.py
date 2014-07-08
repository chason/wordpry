from __future__ import print_function
import requests
import lxml.html
from collections import namedtuple

__version__ = 0.1


class LoginException(Exception):
    pass


Plugin = namedtuple('Plugin', ['name', 'version', 'active'])


class WordPry(object):
    """
    WordPry

    Class to facilitate manipulating WordPress when we don't have a better way.
    """

    def __init__(self, log, pwd, website, ftp_user=None, ftp_pwd=None):
        """
        Creates object and logs into WordPress site, then stores the session.
        :type self: object
        :param log:
        :param pwd:
        :param website:
        :param ftp_user:
        :param ftp_pwd:
        """

        self.log = log
        self.pwd = pwd
        self.website = website

        self.ftp_user = ftp_user
        self.ftp_pwd = ftp_pwd

        self.login_url = None
        self.admin_url = website + "/wp-admin"
        self.plugin_url = self.admin_url + "/plugins.php"

        self._session = self._login()

    def install_plugin(self, plugin):
        """
        Determines which upload method to use, then installs the plugin.
        ``plugin`` should be a file descriptor
        returns plugin info
        """
        s = self._session

        payload = dict(tab='upload')
        page = self._process_page(self.admin_url + "/plugin-install.php",
                                  payload=payload)

        wp_nonce = page.get_element_by_id('_wpnonce').value
        payload = {'_wpnonce': wp_nonce, 'install-plugin-submit': 'Install Now'}
        files = dict(pluginzip=plugin)
        r = s.post(self.admin_url + "/update.php", params=dict(action='upload-plugin'),
                   data=payload, files=files)

        # If there was something wrong with the request, lets raise an exception
        r.raise_for_status()

    def is_plugin_active(self, plugin):
        plugin_list = self.plugin_list
        status = filter(lambda x: (x.name == plugin) and (x.active is True),
                        plugin_list)

        if status:
            return True
        return False

    def activate_plugin(self, plugin):
        """
        Activates plugin.
        ``plugin`` should be identifier for plugin from list_plugins
        returns boolean
        """
        if self.is_plugin_active(plugin):
            raise ValueError("Plugin {0} is already active.".format(plugin))

        page = self._process_page(self.plugin_url)
        plugin_section = page.get_element_by_id(plugin)

        act_link = ''
        # There should only ever be one of these in a plugin section
        activate_span = plugin_section.find_class('activate')[0]
        for child in activate_span.getchildren():
            if child.text == 'Activate':
                act_link = child.get('href')
                break

        if act_link:
            self._process_page("/".join((self.admin_url, act_link)))
        else:
            raise ValueError("Cannot find activate link")

    def deactivate_plugin(self, plugin):
        """
        Deactivates plugin.
        ``plugin`` should be identifier for plugin from list_plugins
        returns boolean
        """
        if not self.is_plugin_active(plugin):
            raise ValueError("Plugin {0} is already inactive.".format(plugin))

        page = self._process_page(self.plugin_url)
        plugin_section = page.get_element_by_id(plugin)

        deact_link = ''
        # There should only be one deactivate link in plugin section
        deact_span = plugin_section.find_class('deactivate')[0]
        for child in deact_span.getchildren():
            if child.text == 'Deactivate':
                deact_link = child.get('href')
                break

        if deact_link:
            self._process_page("/".join((self.admin_url, deact_link)))
        else:
            raise ValueError("Cannot find deactivate link")

    @property
    def plugin_list(self):
        """
        Lists WordPress plugins and their version.
        Returns list of plugins
        """
        plugin_list = []
        plugin_page = self._process_page(self.plugin_url)
        raw_list = plugin_page.get_element_by_id('the-list')
        for elem in raw_list.getchildren():
            name = elem.attrib['id']
            if elem.attrib['class'] == 'active':
                active = True
            else:
                active = False

            # This is janky but all plugins I've seen conform to this schema
            raw_version = elem.find_class('plugin-version-author-uri')[0].text
            version = raw_version.lstrip('Version ').rstrip(' | By')

            plugin_list.append(
                Plugin(name=name, active=active, version=version))

        return plugin_list

    def _login(self):
        """
        :return: requests.Session
        :raise LoginException:
        """
        try:
            s = self._session
        except AttributeError:
            s = requests.Session()

        # Lets get the correct login url
        r = s.get(self.admin_url)
        self.login_url = r.url

        # Setup the headers so the server thinks we're a real browser
        headers = {'Origin': self.website,
                   'Referer': self.admin_url,
                   'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Connection': 'Keep-Alive',
        }
        s.headers.update(headers)

        # Construct payload and POST to login_url
        payload = {'log': self.log,
                   'pwd': self.pwd,
                   'wp-submit': 'Log In',
                   'redirect_to': self.admin_url,
                   'testcookie': 1,
                   'rememberme': 'forever',
        }
        r = s.post(self.login_url, data=payload)
        if r.status_code != 200:
            raise LoginException(
                "Server returned incorrect status code: {}".format(
                    r.status_code))

        auth_cookie = filter(lambda x: x.name.startswith('wordpress_logged_in'),
                             s.cookies)
        if not auth_cookie:
            raise LoginException("No valid authorization cookie from WordPress")

        return s

    def _upload_plugin_ftp(self):
        pass

    def _upload_plugin_http(self):
        pass

    def _process_page(self, page, payload=None):
        s = self._session
        r = s.get(page, params=payload)

        return lxml.html.fromstring(r.content)
