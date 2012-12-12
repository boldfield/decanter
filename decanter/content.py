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
        name = self._name(slug, version, format)
        key = self._key(domain, slug, name)

        content_type = 'text/plain' if format == 'txt' else 'text/html'
        headers = {'Content-Type': content_type}

        key.set_contents_from_string(content, headers=headers)
        key.set_acl('public-read')
        return key

    def get(self, slug, version, format, domain):
        name = self._name(slug, version, format)
        key = self._key(domain, slug, name)
        return key.get_contents_as_string()

    def delete(self, slug, version, format, domain):
        # TODO :: Error handling needs to be more refined
        try:
            name = self._name(slug, version, format)
            key = self._key(domain, slug, name)
            key.delete()
        except:
            return False
        return True

    def version_copy(self, slug, format, domain, from_version, to_version, readable=False):
        # TODO :: Error handling needs to be more refined
        try:
            content = self.get(slug, from_version, format, domain)
            key = self.save(slug, to_version, format, content, domain)
        except:
            return False
        if readable:
            key.set_acl('public-read')
        return True

    def url(self, slug, version, format, domain):
        name = self._name(slug, version, format)
        url = os.path.join(self.s3_url,
                           domain,
                           slug,
                           name)

        return url

    def close(self, *args, **kwargs):
        self.s3.close()

    def _name(self, slug, version, format):
        return '%s-%s.%s' % (slug, version, format)

    def _key(self, domain, slug, name):
        key = os.path.join(domain,
                           slug,
                           name)
        return Key(bucket=self.bucket, name=key)
