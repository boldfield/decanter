import os

import boto
from boto.s3.bucket import Bucket
from boto.s3.key import Key


def init_app(app):
    app.content = S3Content(app)
    app.teardown_appcontext(app.content.close)


class S3Content(object):

    def __init__(self, app):
        self.s3_url = app.config.get('S3_URL')
        self.bucket = app.config.get('S3_BUCKET')

        self.s3 = boto.connect_s3()
        self.bucket = Bucket(self.s3, name=self.bucket)

    def save(self, slug, version, format, content, domain):
        name = self._content_name(slug, version, format)
        key = os.path.join(domain,
                           slug,
                           name)
        key = Key(bucket=self.bucket, name=key)

        content_type = 'text/plain' if format == 'txt' else 'text/html'
        headers = {'Content-Type': content_type}

        key.set_contents_from_string(content, headers=headers)
        key.set_acl('public-read')

    def url(self, slug, version, format, domain):
        name = self._content_name(slug, version, format)
        url = os.path.join(self.s3_url,
                           domain,
                           slug,
                           name)

        return url

    def close(self, *args, **kwargs):
        self.s3.close()

    def _content_name(self, slug, version, format):
        return '%s-v%s.%s' % (slug, version, format)
