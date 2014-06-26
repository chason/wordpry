from __future__ import print_function
import requests

__version__ = 0.1

class WordPry(object):
    """
    WordPry

    Class to facilitate manipulating WordPress when we don't have a better way.
    """

    def init(self, log, pwd, website, ftp_user, ftp_pwd):
        """
        Creates object and logs into WordPress site, then stores the session.
        """
        self.log = log
        self.pwd = pwd
        self.website = website

        self.login_url = None
        self.admin_url = website + "/wp-admin"

        self._session = self._login(log, pwd, website)

    def list_plugins(self):
        """
        Lists WordPress plugins and their version.
        Returns list of plugins
        """
        pass

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

    def _login(self, log, pwd, website):
        s = requests.Session()

    def _upload_plugin_ftp(self):
        pass

    def _upload_plugin_http(self):
        pass
