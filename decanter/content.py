import os

import boto
from boto.s3.bucket import Bucket
from boto.s3.key import Key


def init_app(app):
    app.content = S3Content(app)
    app.image_content = S3Image(app)
    app.teardown_appcontext(app.content.close)
    app.teardown_appcontext(app.image_content.close)


class S3Object(object):

    def __init__(self, app):
        self.s3_url = app.config.get('S3_URL')
        self.bucket = app.config.get('S3_BUCKET')

        self.s3 = boto.connect_s3()
        self.bucket = Bucket(self.s3, name=self.bucket)

    def close(self, *args, **kwargs):
        self.s3.close()


class S3Image(S3Object):

    def save(self, image, name, domain, post=None, make_thumbnail=False):
        headers = {'Content-Type': image.content_type}
        key = self._key(image, name, domain, post=post)

        key.set_contents_from_file(image, headers=headers)
        key.set_acl('public-read')

        return key

    def delete(self, image, name, domain, post=None, make_thumbnail=False):
        # TODO :: Error handling needs to be more refined
        try:
            key = self._key(image, name, domain, post=post)
            key.delete()
            key = self._key(image, name, domain, post=post, thumbnail=True)
            key.delete()
        except:
            return False
        return True

    def _key(self, image, name, domain, post=None, thumbnail=False):
        path = self._path(image, name, domain, post=post, thumbnail=thumbnail)
        return Key(bucket=self.bucket, name=path)

    def url(self, image, name, domain, post=None, thumbnail=False):
        path = self._path(image, name, domain, post=post, thumbnail=thumbnail)
        url = os.path.join(self.s3_url, path)
        return url

    def _path(self, image, name, domain, post=None, thumbnail=False):
        path = domain
        if post is not None:
            path = os.path.join(path, post.slug)

        ext = image.filename.split('.')[-1]
        fname = '%s.%s' % (name, ext)
        if thumbnail:
            fname = '%s-thumb.%s' % (name, ext)

        path = os.path.join(path, 'img', fname)
        return path


class S3Content(S3Object):

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

    def _name(self, slug, version, format):
        return '%s-%s.%s' % (slug, version, format)

    def _key(self, domain, slug, name):
        key = os.path.join(domain,
                           slug,
                           name)
        return Key(bucket=self.bucket, name=key)
