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

    def list_plugins(self):
        """
        Lists WordPress plugins and their version.
        Returns list of plugins
        """
        plugin_list = []
        plugin_page = self._get_page(self.plugin_url)
        raw_list = plugin_page.get_element_by_id('the-list')
        for elem in raw_list.getchildren():
            name = elem.attrib['id']
            if elem.attrib['class'] == 'active':
                active = True

            plugin_list.append(Plugin(name=name, active=active))

    def install_plugin(self, plugin):
        """
        Determines which upload method to use, then installs the plugin.
        ``plugin`` should be a file descriptor
        returns plugin info
        """
        pass

    def activate_plugin(self, plugin):
        """
        Activates plugin.
        ``plugin`` should be identifier for plugin from list_plugins
        returns boolean
        """
        pass

    def deactivate_plugin(self, plugin):
        """
        Deactivates plugin.
        ``plugin`` should be identifier for plugin from list_plugins
        returns boolean
        """
        pass

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

    def _get_page(self, page):
        s = self._session
        r = s.get(page)

        return lxml.html.fromstring(r.content)
