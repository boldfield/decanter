from urlparse import urlparse
from urllib import urlencode
from urllib2 import urlopen, Request, HTTPError
import json


def init_app(app, cdnmanager=None):
    if not cdnmanager:
        app.cdn = CloudFlareCDN(app)
    else:
        app.cdn = cdnmanager(app)


class CloudFlareCDN(object):

    API_URL = 'https://www.cloudflare.com/api_json.html'

    def __init__(self, app):
        self.email = app.config.get('CLOUDFLARE_EMAIL')
        self.api_key = app.config.get('CLOUDFLARE_API_TOKEN')

    def expire_url(self, url):
        # Extract the zone name from the url
        zone = urlparse(url).hostname
        zone = '.'.join(zone.split('.')[-2:])
        data = dict(a='zone_file_purge',
                    tkn=self.api_key,
                    email=self.email,
                    z=zone,
                    url=url)
        r = Request(self.API_URL)
        r.add_data(urlencode(data))

        try:
            resp = urlopen(r)
        except HTTPError, e:
            # Failure should be logged.
            resp = e

        try:
            body = resp.read()
            print body
            resp = json.loads(body)
            success = 'success' == resp['result'] if 'result' in resp else False
        except (ValueError, TypeError):
            success = False

        return success
