import os

from webassets.loaders import YAMLLoader

from flask import Flask
from flask.ext.assets import Environment

from decanter import DIR, settings, restrict, database


class App(Flask):
    url_strict_slashes = True

    def __init__(self, *args, **kw):
        super(App, self).__init__(*args, **kw)
        self.configure()

        self.register_blueprints()
        self.register_assets()

    def configure(self):
        self.url_map.strict_slashes = self.url_strict_slashes

        settings.init_app(self)
        database.init_app(self)
        restrict.init_app(self)

        self.configure_assets()
        self.configure_context()

    def configure_assets(self):
        self.assets = Environment(self)
        self.assets.auto_build = False
        self.assets.directory = os.path.join(DIR, 'assets')
        self.static_folder = os.path.join(DIR, 'static')
        self.assets.manifest = 'file'
        self.assets.url = '/static'

    def register_assets(self):
        manifest = YAMLLoader(os.path.join(DIR, 'assets', 'manifest.yaml'))
        manifest = manifest.load_bundles()
        [self.register_asset_bundle(n, manifest[n]) for n in manifest]

    def register_decanter_assets(self):
        path = os.path.join(DIR, 'assets', 'decanter.yaml')
        if not os.path.isfile(path):
            self._write_decanter_manifest(path)

        manifest = YAMLLoader(path)
        manifest = manifest.load_bundles()
        [self.register_asset_bundle(n, manifest[n]) for n in manifest]

    def _write_decanter_manifest(self, path):
        tmpl_path = os.path.join(DIR, 'assets', 'decanter.yaml.tmpl')
        with open(tmpl_path, 'r') as fp:
            tmpl = fp.read()
        tmpl %= dict(decanter_dir=DIR)
        with open(path, 'w') as fp:
            fp.write(tmpl)
        return True

    def register_blueprints(self):
        pass

    def configure_context(self):
        self.context_processor(self._api_context)

    def register_asset_bundle(self, name, bundle):
        self.assets.register(name, bundle)

    def _api_context(self):
        return dict(api_path=self.config.get('API_PATH'),
                    api_host=self.config.get('API_HOST'))
