from __future__ import with_statement, absolute_import
import re
import sys
import time
import functools
import sqlalchemy
from functools import partial
from operator import itemgetter
from threading import Lock

from sqlalchemy import orm
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.interfaces import (MapperExtension,
                                       SessionExtension,
                                       EXT_CONTINUE)
from sqlalchemy.interfaces import ConnectionProxy
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.util import to_list

from decanter.signals import models_committed, before_models_committed

# the best timer function for the platform
if sys.platform == 'win32':
    _timer = time.clock
else:
    _timer = time.time

_camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')


class UnknownSignalBindError(Exception):
    """Raised when an attempt is made to bind to an unknown
    SQLAlchemy session signal.
    """


def _make_table(db):
    def _make_table(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], db.Column):
            args = (args[0], db.metadata) + args[1:]
        info = kwargs.pop('info', None) or {}
        info.setdefault('bind_key', None)
        kwargs['info'] = info
        return sqlalchemy.Table(*args, **kwargs)
    return _make_table


def _set_default_query_class(d):
    if 'query_class' not in d:
        d['query_class'] = BaseQuery


def _wrap_with_default_query_class(fn):
    @functools.wraps(fn)
    def newfn(*args, **kwargs):
        _set_default_query_class(kwargs)
        if "backref" in kwargs:
            backref = kwargs['backref']
            if isinstance(backref, basestring):
                backref = (backref, {})
            _set_default_query_class(backref[1])
        return fn(*args, **kwargs)
    return newfn


def _include_sqlalchemy(obj):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))
    # Note: obj.Table does not attempt to be a SQLAlchemy Table class.
    obj.Table = _make_table(obj)
    obj.mapper = signalling_mapper
    obj.relationship = _wrap_with_default_query_class(obj.relationship)
    obj.relation = _wrap_with_default_query_class(obj.relation)
    obj.dynamic_loader = _wrap_with_default_query_class(obj.dynamic_loader)


class _DebugQueryTuple(tuple):
    statement = property(itemgetter(0))
    parameters = property(itemgetter(1))
    start_time = property(itemgetter(2))
    end_time = property(itemgetter(3))
    context = property(itemgetter(4))

    @property
    def duration(self):
        return self.end_time - self.start_time

    def __repr__(self):
        return '<query statement="%s" parameters=%r duration=%.03f>' % (
            self.statement,
            self.parameters,
            self.duration
        )


def _calling_context(app_path):
    frm = sys._getframe(1)
    while frm.f_back is not None:
        name = frm.f_globals.get('__name__')
        if name and (name == app_path or name.startswith(app_path + '.')):
            funcname = frm.f_code.co_name
            return '%s:%s (%s)' % (
                frm.f_code.co_filename,
                frm.f_lineno,
                funcname
            )
        frm = frm.f_back
    return '<unknown>'


class _ConnectionDebugProxy(ConnectionProxy):
    """Helps debugging the database."""

    def __init__(self, import_name, context=None):
        self.package_name = import_name
        self.context = context

    def cursor_execute(self, execute, cursor, statement, parameters,
                       context, executemany):
        start = _timer()
        try:
            return execute(cursor, statement, parameters, context)
        finally:
            if context is None:
                return
            queries = getattr(context, 'sqlalchemy_queries', None)
            if queries is None:
                queries = []
                setattr(context, 'sqlalchemy_queries', queries)
            queries.append(_DebugQueryTuple((
                statement, parameters, start, _timer(),
                _calling_context(self.package_name))))


class _SignalTrackingMapperExtension(MapperExtension):

    def after_delete(self, mapper, connection, instance):
        return self._record(mapper, instance, 'delete')

    def after_insert(self, mapper, connection, instance):
        return self._record(mapper, instance, 'insert')

    def after_update(self, mapper, connection, instance):
        return self._record(mapper, instance, 'update')

    def _record(self, mapper, model, operation):
        pk = tuple(mapper.primary_key_from_instance(model))
        orm.object_session(model)._model_changes[pk] = (model, operation)
        return EXT_CONTINUE


class _SignallingSessionExtension(SessionExtension):

    def __init__(self, *args, **kwargs):
        super(_SignallingSessionExtension, self).__init__(*args, **kwargs)
        self._models_committed = []
        self._before_models_committed = []

    def before_commit(self, session):
        d = session._model_changes
        if d:
            before_models_committed.send(session, changes=d.values())
        return EXT_CONTINUE

    def after_commit(self, session):
        d = session._model_changes
        if d:
            models_committed.send(session, changes=d.values())
            d.clear()
        return EXT_CONTINUE

    def after_rollback(self, session):
        session._model_changes.clear()
        return EXT_CONTINUE


class _SignallingSession(Session):

    def __init__(self, db, autocommit=False, autoflush=False, **options):
        self.db = db
        self._model_changes = {}
        Session.__init__(self, autocommit=autocommit, autoflush=autoflush,
                         extension=db.session_extensions,
                         bind=db.engine,
                         binds=db.get_binds(), **options)

    def get_bind(self, mapper, clause=None):
        # mapper is None if someone tries to just get a connection
        if mapper is not None:
            info = getattr(mapper.mapped_table, 'info', {})
            bind_key = info.get('bind_key')
            if bind_key is not None:
                state = get_state(self.db)
                return state.db.get_engine(self.app, bind=bind_key)
        return Session.get_bind(self, mapper, clause)


class BaseQuery(orm.Query):
    """The default query object used for models, and exposed as
    :attr:`~SQLAlchemy.Query`. This can be subclassed and
    replaced for individual models by setting the :attr:`~Model.query_class`
    attribute.  This is a subclass of a standard SQLAlchemy
    :class:`~sqlalchemy.orm.query.Query` class and has all the methods of a
    standard query as well.
    """


class _QueryProperty(object):

    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            mapper = orm.class_mapper(type)
            if mapper:
                return type.query_class(mapper, session=self.sa.session())
        except UnmappedClassError:
            return None


def _record_queries(sa):
    if sa.config.get('DEBUG'):
        return True
    rq = sa.config.get('SQLALCHEMY_RECORD_QUERIES')
    return rq if rq else False


class _EngineConnector(object):

    def __init__(self, sa, bind=None):
        self._sa = sa
        self._engine = None
        self._connected_for = None
        self._bind = bind
        self._lock = Lock()

    def get_uri(self):
        if self._bind is None:
            return self._sa.config.get('SQLALCHEMY_DATABASE_URI')
        binds = self._sa.config.get('SQLALCHEMY_BINDS') or ()
        assert self._bind in binds, \
            'Bind %r is not specified.  Set it in the SQLALCHEMY_BINDS ' \
            'configuration variable' % self._bind
        return binds[self._bind]

    def get_engine(self):
        with self._lock:
            uri = self.get_uri()
            echo = self._sa.config.get('SQLALCHEMY_ECHO')
            if (uri, echo) == self._connected_for:
                return self._engine
            info = make_url(uri)
            options = {'convert_unicode': True}
            self._sa.apply_pool_defaults(options)
            self._sa.apply_driver_hacks(info, options)
            if _record_queries(self._sa):
                # The argument to _ConnectionDebugProxy should be the import
                # name of a package... the question is, which package...
                name = 'SQLAlchemy Engine Connector'
                options['proxy'] = _ConnectionDebugProxy(name)
            if echo:
                options['echo'] = True
            self._engine = rv = sqlalchemy.create_engine(info, **options)
            self._connected_for = (uri, echo)
            return rv


def _defines_primary_key(d):
    """Figures out if the given dictonary defines a primary key column."""
    return any(v.primary_key for k, v in d.iteritems()
               if isinstance(v, sqlalchemy.Column))


class _BoundDeclarativeMeta(DeclarativeMeta):

    def __new__(cls, name, bases, d):
        tablename = d.get('__tablename__')

        # generate a table name automatically if it's missing and the
        # class dictionary declares a primary key.  We cannot always
        # attach a primary key to support model inheritance that does
        # not use joins.  We also don't want a table name if a whole
        # table is defined
        if not tablename and d.get('__table__') is None and _defines_primary_key(d):
            def _join(match):
                word = match.group()
                if len(word) > 1:
                    return ('_%s_%s' % (word[:-1], word[-1])).lower()
                return '_' + word.lower()
            d['__tablename__'] = _camelcase_re.sub(_join, name).lstrip('_')

        return DeclarativeMeta.__new__(cls, name, bases, d)

    def __init__(self, name, bases, d):
        bind_key = d.pop('__bind_key__', None)
        DeclarativeMeta.__init__(self, name, bases, d)
        if bind_key is not None:
            self.__table__.info['bind_key'] = bind_key


def get_state(db):
    """Gets the state for the application"""
    assert 'sqlalchemy' in db.extensions, \
        'The sqlalchemy extension was not registered to the current ' \
        'application.  Please make sure to call init_app() first.'
    return db.extensions['sqlalchemy']


def signalling_mapper(*args, **kwargs):
    """Replacement for mapper that injects some extra extensions"""
    extensions = to_list(kwargs.pop('extension', None), [])
    extensions.append(_SignalTrackingMapperExtension())
    kwargs['extension'] = extensions
    return sqlalchemy.orm.mapper(*args, **kwargs)


class _SQLAlchemyState(object):
    """Remembers configuration for the (db, app) tuple."""

    def __init__(self, db):
        self.db = db
        self.connectors = {}


class Model(object):
    """Baseclass for custom user models."""

    #: the query class used.  The :attr:`query` attribute is an instance
    #: of this class.  By default a :class:`BaseQuery` is used.
    query_class = BaseQuery

    #: an instance of :attr:`query_class`.  Can be used to query the
    #: database for instances of this model.
    query = None


class Database(object):

    def __init__(self, config=None, use_native_unicode=True,
                 session_extensions=None, session_options=None,
                 base_query_class=BaseQuery):
        self.config = config
        self.use_native_unicode = use_native_unicode
        self.session_extensions = to_list(session_extensions, []) + \
            [_SignallingSessionExtension()]

        if session_options is None:
            session_options = {}

        self.session = self.create_scoped_session(session_options)
        self.Model = self.make_declarative_base()
        self._engine_lock = Lock()

        _include_sqlalchemy(self)
        self.Query = base_query_class

    @property
    def metadata(self):
        """Returns the metadata"""
        return self.Model.metadata

    def create_scoped_session(self, options=None):
        """Helper factory method that creates a scoped session."""
        if options is None:
            options = {}
        return orm.scoped_session(
            partial(_SignallingSession, self, **options)
        )

    def make_declarative_base(self):
        """Creates the declarative base."""
        base = declarative_base(cls=Model, name='Model',
                                mapper=signalling_mapper,
                                metaclass=_BoundDeclarativeMeta)
        base.query = _QueryProperty(self)
        return base

    def init_connection(self, config):
        """This callback can be used to initialize an application for the
        use with this database setup.  Never use a database in the context
        of an application not initialized that way or connections will
        leak.
        """
        if not self.config:
            self.config = dict()
        self.config.update(config)

        self.config.setdefault('SQLALCHEMY_BINDS', None)
        self.config.setdefault('SQLALCHEMY_NATIVE_UNICODE', None)
        self.config.setdefault('SQLALCHEMY_ECHO', False)
        self.config.setdefault('SQLALCHEMY_RECORD_QUERIES', None)
        self.config.setdefault('SQLALCHEMY_POOL_SIZE', None)
        self.config.setdefault('SQLALCHEMY_POOL_TIMEOUT', None)
        self.config.setdefault('SQLALCHEMY_POOL_RECYCLE', None)

        if not hasattr(self, 'extensions'):
            self.extensions = {}
        self.extensions['sqlalchemy'] = _SQLAlchemyState(self)

        ## 0.9 and later
        #if hasattr(app, 'teardown_appcontext'):
        #    teardown = app.teardown_appcontext
        ## 0.7 to 0.8
        #elif hasattr(app, 'teardown_request'):
        #    teardown = app.teardown_request
        ## Older Flask versions
        #else:
        #    teardown = app.after_request

        #@teardown
        #def shutdown_session(response):
        #    self.session.remove()
        #    return response

    def shutdown_session(self):
        self.session.remove()

    def apply_pool_defaults(self, options):
        def _setdefault(optionkey, configkey):
            value = self.config.get(configkey)
            if value is not None:
                options[optionkey] = value
        _setdefault('pool_size', 'SQLALCHEMY_POOL_SIZE')
        _setdefault('pool_timeout', 'SQLALCHEMY_POOL_TIMEOUT')
        _setdefault('pool_recycle', 'SQLALCHEMY_POOL_RECYCLE')

    def apply_driver_hacks(self, info, options):
        """This method is called before engine creation and used to inject
        driver specific hacks into the options.  The `options` parameter is
        a dictionary of keyword arguments that will then be used to call
        the :func:`sqlalchemy.create_engine` function.

        The default implementation injects the setting of
        `SQLALCHEMY_NATIVE_UNICODE`.
        """
        unu = self.config.get('SQLALCHEMY_NATIVE_UNICODE')
        if unu is None:
            unu = self.use_native_unicode
        if not unu:
            options['use_native_unicode'] = False

    @property
    def engine(self):
        """Gives access to the engine.  If the database configuration is bound
        to a specific application (initialized with an application) this will
        always return a database connection.  If however the current
        application is used this might raise a :exc:`RuntimeError` if no
        application is active at the moment.
        """
        return self.get_engine()

    def make_connector(self, bind=None):
        """Creates the connector for a given state and bind."""
        return _EngineConnector(self, bind)

    def get_engine(self, bind=None):
        """Returns a specific engine.

        .. versionadded:: 0.12
        """
        with self._engine_lock:
            state = get_state(self)
            connector = state.connectors.get(bind)
            if connector is None:
                connector = self.make_connector(bind)
                state.connectors[bind] = connector
            return connector.get_engine()

    def get_tables_for_bind(self, bind=None):
        """Returns a list of all tables relevant for a bind."""
        result = []
        for table in self.Model.metadata.tables.itervalues():
            if table.info.get('bind_key') == bind:
                result.append(table)
        return result

    def get_binds(self):
        """Returns a dictionary with a table->engine mapping.

        This is suitable for use of sessionmaker(binds=db.get_binds(app)).
        """
        binds = [None] + list(self.config.get('SQLALCHEMY_BINDS') or ())
        retval = {}
        for bind in binds:
            engine = self.get_engine(bind)
            tables = self.get_tables_for_bind(bind)
            retval.update(dict((table, engine) for table in tables))
        return retval

    def _execute_for_all_tables(self, bind, operation):
        if bind == '__all__':
            binds = [None] + list(self.config.get('SQLALCHEMY_BINDS') or ())
        elif isinstance(bind, basestring):
            binds = [bind]
        else:
            binds = bind

        for bind in binds:
            tables = self.get_tables_for_bind(bind)
            op = getattr(self.Model.metadata, operation)
            op(bind=self.get_engine(bind), tables=tables)

    def create_all(self, bind='__all__'):
        """Creates all tables.

        .. versionchanged:: 0.12
           Parameters were added
        """
        self._execute_for_all_tables(bind, 'create_all')

    def drop_all(self, bind='__all__'):
        """Drops all tables.

        .. versionchanged:: 0.12
           Parameters were added
        """
        self._execute_for_all_tables(bind, 'drop_all')

    def reflect(self, bind='__all__'):
        """Reflects tables from the database.

        .. versionchanged:: 0.12
           Parameters were added
        """
        self._execute_for_all_tables(bind, 'reflect')

    def __repr__(self):
        return '<%s engine=%r>' % (
            self.__class__.__name__,
            self.config.get('SQLALCHEMY_DATABASE_URI')
        )
