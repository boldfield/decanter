import os

from werkzeug.exceptions import NotFound

from decanter.dispatch import SubdomainDispatcher
from decanter.app import (create_app as create_web_app,
                          register_blueprints as register_om_blueprints)
from decanter.api import (create_app as create_api_app,
                          register_blueprints as register_api_blueprints)

DIR = os.path.abspath(__file__)
DIR = os.path.dirname(DIR)

# TODO : These should be in settings.
SUPPORTED_SUBDOMAINS = ('api', 'www', '')
SUBDOMAIN_MAP = {'api': create_api_app,
                 'www': create_web_app,
                 '': create_web_app}
BLUEPRINT_MAP = {'api': register_api_blueprints,
                 'www': register_om_blueprints,
                 '': register_om_blueprints}


def create_app(subdomain):
    if not subdomain in SUPPORTED_SUBDOMAINS:
        # We can then just return the NotFound() exception as
        # application which will render a default 404 page.
        return NotFound()

    # Default to OptionMinder App
    create_app = SUBDOMAIN_MAP.get(subdomain, create_web_app)
    app = create_app()

    # Register view blueprints
    register_blueprints = BLUEPRINT_MAP.get(subdomain, register_om_blueprints)
    register_blueprints(app)

    # Register login manager
    #app.pwd_context = PWD_CONTEXT

    return app

app = SubdomainDispatcher(create_app)
