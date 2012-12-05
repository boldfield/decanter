var kohelpers, _ref, _ref1, _ref2, _ref3,
  __slice = [].slice,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

kohelpers = window.kohelpers = (_ref = window.kohelpers) != null ? _ref : {};

ko.extenders.validate = function(target, opts) {
  var exists, index, validator, _i, _len, _ref1, _ref2, _ref3, _ref4;
  if (opts == null) {
    opts = [];
  }
  exists = target.validate != null;
  if ((_ref1 = target.errors) == null) {
    target.errors = ko.observableArray([]);
  }
  if ((_ref2 = target.error) == null) {
    target.error = ko.computed(function() {
      var _ref3;
      return (_ref3 = target.errors()) != null ? _ref3[0] : void 0;
    });
  }
  if ((_ref3 = target.validators) == null) {
    target.validators = [];
  }
  for (_i = 0, _len = opts.length; _i < _len; _i++) {
    validator = opts[_i];
    index = target.validators.indexOf(validator);
    if (index < 0) {
      target.validators.push(validator);
    }
  }
  if ((_ref4 = target.validate) == null) {
    target.validate = function(value) {
      var errors, v, _j, _len1, _ref5;
      errors = [];
      _ref5 = target.validators;
      for (_j = 0, _len1 = _ref5.length; _j < _len1; _j++) {
        v = _ref5[_j];
        errors = errors.concat(v.errors(value != null ? value : target()));
      }
      target.errors(errors);
      return errors;
    };
  }
  if (!exists) {
    target.subscribe(target.validate);
  }
  return target;
};

ko.extenders.track = function(target, enabled) {
  var _ref1, _ref2, _ref3, _ref4;
  target.tracking = enabled !== false;
  if ((_ref1 = target.history) == null) {
    target.history = ko.observableArray([target()]);
  }
  if ((_ref2 = target.previous) == null) {
    target.previous = ko.computed(function() {
      var _ref3;
      return (_ref3 = target.history()) != null ? _ref3[0] : void 0;
    });
  }
  if ((_ref3 = target.dirty) == null) {
    target.dirty = ko.computed(function() {
      var _ref4;
      return target() === ((_ref4 = target.history()) != null ? _ref4[0] : void 0);
    });
  }
  return (_ref4 = target.commit) != null ? _ref4 : target.commit = function() {
    var value;
    value = target();
    if (target.history.indexOf(value) !== 0) {
      target.history.unshift(target());
    }
    return target;
  };
};

if ((_ref1 = kohelpers.form) == null) {
  kohelpers.form = {};
}

kohelpers.form.Field = (function() {

  function Field(config) {
    var validator, _i, _len, _ref2, _ref3,
      _this = this;
    if (config == null) {
      config = {};
    }
    this.config = config;
    if (config.name != null) {
      this.name = config.name;
    }
    if (!this.name) {
      throw 'A field must have a name';
    }
    if (ko.isObservable(config.value)) {
      this.value = config.value;
    } else {
      if (config.value != null) {
        this.value = ko.observable(config.value);
      }
      if (config.value == null) {
        this.value = ko.observable(this["default"]);
      }
    }
    if (config.remote != null) {
      this.remote = config.remote;
    }
    if (this.remote == null) {
      this.remote = this.name;
    }
    if (config.label != null) {
      this.label = config.label;
    }
    this.filter = config.filter;
    if (config["default"] != null) {
      this["default"] = config["default"];
    }
    this.error = ko.observable();
    this.errors = ko.observableArray([]);
    this.errors.subscribe(this.onErrors, this);
    this.valid = ko.observable();
    this.validating = ko.observable();
    this.title = ko.computed(this.title, this);
    this.disabled = ko.observable(false);
    this.validators = (_ref2 = config.validators) != null ? _ref2 : [];
    if (this.label) {
      _ref3 = this.validators;
      for (_i = 0, _len = _ref3.length; _i < _len; _i++) {
        validator = _ref3[_i];
        validator.name = this.label;
      }
    }
    this.value.error = this.error;
    this.value.errors = this.errors;
    this.value.valid = this.valid;
    this.value.validating = this.validating;
    this.value.field = this;
    this.value.title = this.title;
    this.value.validate = function() {
      return _this.validate();
    };
    this.value.empty = function() {
      return _this.empty();
    };
    this.value.reset = function() {
      var args;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      return _this.reset.apply(_this, args);
    };
    this.value.subscribe(this.onChanged, this);
  }

  Field.prototype.title = function() {
    return this.error() || this.label || this.name;
  };

  Field.prototype.validate = function(value, validators, deferred) {
    var validator,
      _this = this;
    if (deferred == null) {
      deferred = $.Deferred();
    }
    if (arguments.length === 0 && (this.valid() != null)) {
      deferred.resolve(this);
      return deferred;
    }
    if (value == null) {
      value = this.value();
    }
    if (validators == null) {
      validators = this.validators.slice();
    }
    if (validators.length < 1) {
      if (this.validating()) {
        this.validating(false);
      }
      this.errors([]);
      deferred.resolve(this);
      return deferred;
    }
    if (!this.validating()) {
      this.validating(true);
    }
    validator = validators.shift();
    validator.validate(value).done(function(error) {
      if (error) {
        if (_this.validating()) {
          _this.validating(false);
        }
        _this.errors([error]);
        deferred.resolve(_this);
      }
      if (!error && _this.validating) {
        return _this.validate(value, validators, deferred);
      }
    });
    return deferred;
  };

  Field.prototype.onErrors = function(errors) {
    var error;
    if (this.disabled()) {
      return;
    }
    if (errors == null) {
      errors = this.errors();
    }
    error = errors != null ? errors[0] : void 0;
    this.error(error);
    return this.valid(!(error != null));
  };

  Field.prototype.onChanged = function(value) {
    if (this.validating() || this.disabled()) {
      return;
    }
    if (value == null) {
      value = this.value();
    }
    if ((this["default"] != null) && ((!(value != null)) || value === '')) {
      this.disabled(true);
      value = this["default"];
      this.value(this["default"]);
      this.disabled(false);
    }
    return this.validate(value);
  };

  Field.prototype.empty = function() {
    return this.reset(void 0);
  };

  Field.prototype.reset = function(value) {
    this.disabled(true);
    if (!(arguments.length < 1)) {
      this.value(value);
    }
    this.errors([]);
    this.error(void 0);
    return this.disabled(false);
  };

  return Field;

})();

kohelpers.form.Form = (function() {

  Form.prototype.autosave = true;

  Form.prototype.saveDelay = -1;

  Form.prototype.responseDelay = -1;

  function Form(config) {
    this.submit = __bind(this.submit, this);

    var _this = this;
    if (config == null) {
      config = {};
    }
    this.config = config;
    this.fields = [];
    this.method = config.method || 'POST';
    if (this.config.autosave != null) {
      this.autosave = this.config.autosave;
    }
    if (this.config.saveDelay != null) {
      this.saveDelay = this.config.saveDelay;
    }
    if (this.config.responseDelay != null) {
      this.responseDelay = this.config.responseDelay;
    }
    this.submitted = new signals.Signal();
    this.saved = new signals.Signal();
    this.failed = new signals.Signal();
    this.saving = ko.observable(false);
    this.processing = ko.observable(false);
    this.invalids = ko.observableArray([]);
    this.invalid = ko.observable();
    this.errors = ko.observableArray([]);
    this.error = ko.observable();
    this.invalids.subscribe(function(invalids) {
      _this.invalid(invalids != null ? invalids[0] : void 0);
      return _this.populateErrors();
    });
    this.errors.subscribe(function(errors) {
      return _this.error(errors != null ? errors[0] : void 0);
    });
    this.init(config);
  }

  Form.prototype.populateInvalid = function() {
    var f, invalids;
    if (this._validating) {
      return;
    }
    invalids = (function() {
      var _i, _len, _ref2, _results;
      _ref2 = this.fields;
      _results = [];
      for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
        f = _ref2[_i];
        if (this[f].error()) {
          _results.push(this[f]);
        }
      }
      return _results;
    }).call(this);
    return this.invalids(invalids);
  };

  Form.prototype.populateErrors = function(invalids) {
    var errors, i;
    if (this._validating) {
      return;
    }
    if (invalids == null) {
      invalids = this.invalids();
    }
    errors = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = invalids.length; _i < _len; _i++) {
        i = invalids[_i];
        _results.push(i.error());
      }
      return _results;
    })();
    return this.errors(errors);
  };

  Form.prototype.isInvalid = function(field) {
    if (this[field] != null) {
      return this.invalid() === this[field];
    }
    return this.invalid() === field;
  };

  Form.prototype.field = function(field) {
    var exists;
    if (!(field instanceof kohelpers.form.Field)) {
      field = new kohelpers.form.Field(field);
    }
    if (!(this.fields.indexOf(field.name) > -1)) {
      this.fields.push(field.name);
    }
    exists = this[field.name] != null;
    if (!exists) {
      this[field.name] = field.value;
    }
    if (!exists) {
      this[field.name].error.subscribe(this.populateInvalid, this);
    }
    return this[field.name];
  };

  Form.prototype.validate = function() {
    var deferred, deferreds, field,
      _this = this;
    if (this._validating) {
      return;
    }
    this._validating = true;
    deferred = $.Deferred();
    deferreds = (function() {
      var _i, _len, _ref2, _results;
      _ref2 = this.fields;
      _results = [];
      for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
        field = _ref2[_i];
        _results.push(this[field].validate());
      }
      return _results;
    }).call(this);
    $.when.apply($, deferreds).done(function() {
      _this._validating = false;
      _this.populateInvalid();
      return deferred.resolve(_this.invalids().length < 1);
    });
    return deferred;
  };

  Form.prototype.csrf = function() {
    return $('head:first > meta[name=csrf-token]:first').attr('content');
  };

  Form.prototype.empty = function() {
    var field, _i, _len, _ref2;
    _ref2 = this.fields;
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      field = _ref2[_i];
      this[field].empty();
    }
    return this;
  };

  Form.prototype.reset = function(values) {
    var field, hasValue, _i, _len, _ref2;
    if (values == null) {
      values = {};
    }
    _ref2 = this.fields;
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      field = _ref2[_i];
      hasValue = values.hasOwnProperty(field);
      if (hasValue) {
        this[field].reset(values[field]);
      }
      if (!hasValue) {
        this[field].reset();
      }
    }
    return this;
  };

  Form.prototype.submit = function() {
    var _this = this;
    this.validate().done(function(valid) {
      if (!valid) {
        return;
      }
      _this.submitted.dispatch(_this);
      if (_this.autosave) {
        return _this.save();
      }
    });
    return this;
  };

  Form.prototype.save = function() {
    var callback, csrf, data, endpoint, headers,
      _this = this;
    if (this.saving()) {
      return this;
    }
    this.saving(true);
    csrf = this.csrf();
    headers = {};
    if (csrf) {
      headers['X-CSRFToken'] = csrf;
    }
    endpoint = this.endpoint;
    data = this.todict();
    this.processing(true);
    callback = function() {
      return $.ajax({
        context: _this,
        data: JSON.stringify(data),
        mimeType: 'application/json',
        contentType: 'application/json',
        dataType: 'json',
        error: _this.onError,
        headers: headers,
        success: _this.onSuccess,
        type: _this.method,
        url: endpoint
      });
    };
    if (!(this.saveDelay > -1)) {
      callback();
    }
    if (this.saveDelay > -1) {
      setTimeout(callback, this.saveDelay);
    }
    return this;
  };

  Form.prototype.setJsonMimeType = function(request) {
    if (request && request.overrideMimeType) {
      return request.overrideMimeType("application/json;charset=UTF-8");
    }
  };

  Form.prototype.onSuccess = function(value, message, xhr) {
    var callback,
      _this = this;
    callback = function() {
      _this.processing(false);
      _this.saved.dispatch(_this, xhr, value);
      return setTimeout((function() {
        return _this.saving(false);
      }), 2);
    };
    if (this.responseDelay > -1) {
      callback();
    }
    if (!(this.responseDelay > -1)) {
      return setTimeout(callback, this.responseDelay);
    }
  };

  Form.prototype.onError = function(xhr, message, value) {
    var callback,
      _this = this;
    callback = function() {
      var txt;
      _this.processing(false);
      txt = 'An error occurred';
      if (xhr.status === 403) {
        txt = xhr.responseText;
      }
      _this.error(txt);
      _this.failed.dispatch(_this, xhr, value);
      return _this.saving(false);
    };
    if (!(this.responseDelay > -1)) {
      callback();
    }
    if (this.responseDelay > -1) {
      return setTimeout(callback, this.responseDelay);
    }
  };

  Form.prototype.todict = function() {
    var arg, args, dict, field, fields, key, value, _i, _j, _len, _len1;
    args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
    fields = [];
    dict = {};
    if (args.length < 1) {
      fields = this.fields;
    } else {
      for (_i = 0, _len = args.length; _i < _len; _i++) {
        arg = args[_i];
        if (this.fields.indexOf(arg) > -1) {
          fields.push(arg);
        }
      }
      if (fields.length < 1) {
        return dict;
      }
    }
    for (_j = 0, _len1 = fields.length; _j < _len1; _j++) {
      field = fields[_j];
      if (this[field].field.filter) {
        continue;
      }
      key = this[field].field.remote;
      value = this[field]();
      if (value != null) {
        dict[key] = value;
      }
    }
    return dict;
  };

  return Form;

})();

if ((_ref2 = kohelpers.model) == null) {
  kohelpers.model = {};
}

kohelpers.model.Schema = (function() {

  function Schema(cls, mapping) {
    if (!jQuery.isFunction(cls)) {
      mapping = cls;
      cls = void 0;
    }
    this.model = cls;
    this.mapping = mapping != null ? mapping : {};
  }

  Schema.prototype.key = function(key, callback) {
    var _base, _ref3;
    if (key && callback) {
      if ((_ref3 = (_base = this.mapping)[key]) == null) {
        _base[key] = {};
      }
      this.mapping[key].key = callback;
    }
    return this;
  };

  Schema.prototype.map = function(key, callback) {
    var _base, _ref3;
    if (key && callback) {
      if ((_ref3 = (_base = this.mapping)[key]) == null) {
        _base[key] = {};
      }
      this.mapping[key].create = callback;
      this.mapping[key].update = callback;
    }
    return this;
  };

  Schema.prototype.mapMoment = function() {
    var key, keys, _i, _len, _results;
    keys = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
    _results = [];
    for (_i = 0, _len = keys.length; _i < _len; _i++) {
      key = keys[_i];
      _results.push(this.map(key, function(context) {
        var m;
        m = moment(context.data);
        if (context.observable) {
          return m;
        }
        return ko.observable(m);
      }));
    }
    return _results;
  };

  Schema.prototype.update = function(key, callback) {
    var _base, _ref3;
    if (key && callback) {
      if ((_ref3 = (_base = this.mapping)[key]) == null) {
        _base[key] = {};
      }
      this.mapping[key].update = callback;
    }
    return this;
  };

  Schema.prototype.addList = function() {
    var arg, args, key, _base, _i, _len, _ref3;
    key = arguments[0], args = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
    if (!(args.length > 0)) {
      return this;
    }
    if ((_ref3 = (_base = this.mapping)[key]) == null) {
      _base[key] = [];
    }
    for (_i = 0, _len = args.length; _i < _len; _i++) {
      arg = args[_i];
      if (jQuery.isArray(arg)) {
        arg = arg.slice();
        arg.unshift(key);
        this.addList.apply(this, arg);
      } else {
        this.mapping[key].push(arg);
      }
    }
    if (this.mapping[key].length < 1) {
      delete this.mapping[key];
    }
    return this;
  };

  Schema.prototype.ignore = function() {
    var args;
    args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
    args.unshift('ignore');
    this.addList.apply(this, args);
    return this;
  };

  Schema.prototype.include = function() {
    var args;
    args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
    args.unshift('include');
    this.addList.apply(this, args);
    return this;
  };

  Schema.prototype.copy = function() {
    var args;
    args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
    args.unshift('copy');
    this.addList.apply(this, args);
    return this;
  };

  Schema.prototype.load = function(data, viewModel, onUpdate) {
    var field, fields, k, v, _i, _len;
    if (!viewModel && this.model) {
      viewModel = this.model();
    }
    if (!viewModel) {
      return ko.mapping.fromJS(data, this.mapping);
    }
    ko.mapping.fromJS(data, this.mapping, viewModel);
    fields = [];
    for (k in data) {
      v = data[k];
      fields.push(k);
    }
    viewModel.fields = fields;
    if (onUpdate) {
      for (_i = 0, _len = fields.length; _i < _len; _i++) {
        field = fields[_i];
        viewModel[field].subscribe(onUpdate);
      }
    }
    return viewModel;
  };

  Schema.prototype.dump = function(viewModel, fields) {
    var data, filter;
    filter = function(fields) {
      var field, filtered, _i, _len;
      filtered = {};
      for (_i = 0, _len = fields.length; _i < _len; _i++) {
        field = fields[_i];
        filtered[field] = viewModel[field];
      }
      return filtered;
    };
    if (fields) {
      data = filter(fields);
    }
    if (!data) {
      data = viewModel;
    }
    if (data) {
      return ko.mapping.toJS(data);
    }
  };

  return Schema;

})();

kohelpers.model.schema = new kohelpers.model.Schema();

kohelpers.model.Model = (function() {

  Model.load = function(data) {
    return new this(data);
  };

  function Model(data) {
    this.onValueUpdate = __bind(this.onValueUpdate, this);

    var _ref3;
    this.updated = ko.observable(false);
    this.schema = (_ref3 = this.constructor.schema) != null ? _ref3 : kohelpers.model.schema;
    this.schema.load(data, this, this.onValueUpdate);
    this.saved = new signals.Signal();
    this.failed = new signals.Signal();
    this.saving = ko.observable(false);
    this.processing = ko.observable(false);
  }

  Model.prototype.update = function(data) {
    this.schema.load(data, this, this.onValueUpdate);
    return this;
  };

  Model.prototype.dump = function() {
    return this.schema.dump(this, this.fields);
  };

  Model.prototype.toJSON = function() {
    return ko.toJSON(this.schema.dump(this, this.fields));
  };

  Model.prototype.onValueUpdate = function() {
    return this.updated(true);
  };

  Model.prototype.save = function() {
    var callback, endpoint, headers,
      _this = this;
    if (this.saving()) {
      return this;
    }
    if (!this.updated()) {
      return this;
    }
    this.saving(true);
    this.processing(true);
    headers = {};
    endpoint = this.endpoint;
    callback = function() {
      return jQuery.ajax({
        context: _this,
        mimeType: 'application/json',
        contentType: 'application/json',
        dataType: 'json',
        data: _this.toJSON(),
        error: _this.onError,
        headers: headers,
        success: _this.onSuccess,
        type: 'PUT',
        url: endpoint
      });
    };
    callback();
    return this;
  };

  Model.prototype.onError = function(xhr, message, value) {
    var callback,
      _this = this;
    callback = function() {
      _this.processing(false);
      _this.saving(false);
      return _this.failed.dispatch(_this, xhr, value);
    };
    return callback();
  };

  Model.prototype.onSuccess = function(value, message, xhr) {
    var callback,
      _this = this;
    callback = function() {
      _this.processing(false);
      _this.saving(false);
      return _this.saved.dispatch(_this, xhr, value);
    };
    return callback();
  };

  return Model;

})();

kohelpers.model.ModelContainer = (function() {

  ModelContainer.model = void 0;

  ModelContainer.endpoint = void 0;

  function ModelContainer(config) {
    this.commitUpdated = __bind(this.commitUpdated, this);
    if (config == null) {
      config = {};
    }
    this.config = config;
    this.loaded = new signals.Signal();
    this.failed = new signals.Signal();
    this.loading = ko.observable(false);
    this.processing = ko.observable(false);
    this.models = ko.observableArray([]);
    this.modelIds = ko.observableArray([]);
  }

  ModelContainer.prototype.load = function() {
    var callback, endpoint, headers,
      _this = this;
    if (this.loading()) {
      return this;
    }
    this.loading(true);
    this.processing(true);
    headers = {};
    endpoint = this.endpoint;
    callback = function() {
      return $.ajax({
        context: _this,
        mimeType: 'application/json',
        contentType: 'application/json',
        error: _this.onError,
        headers: headers,
        success: _this.onSuccess,
        type: 'GET',
        url: endpoint
      });
    };
    callback();
    return this;
  };

  ModelContainer.prototype.onError = function(xhr, message, value) {
    var callback,
      _this = this;
    callback = function() {
      _this.processing(false);
      _this.failed.dispatch(_this, xhr, value);
      return _this.loading(false);
    };
    return callback();
  };

  ModelContainer.prototype.onSuccess = function(value, message, xhr) {
    var callback,
      _this = this;
    callback = function() {
      var item, m, _i, _len, _results;
      _this.processing(false);
      _this.loaded.dispatch(_this, xhr, value);
      _results = [];
      for (_i = 0, _len = value.length; _i < _len; _i++) {
        item = value[_i];
        m = new _this.model(item);
        _results.push(_this.models.push(m));
      }
      return _results;
    };
    return callback();
  };

  ModelContainer.prototype.commitUpdated = function() {
    var model, _i, _len, _ref3, _results;
    _ref3 = this.models();
    _results = [];
    for (_i = 0, _len = _ref3.length; _i < _len; _i++) {
      model = _ref3[_i];
      _results.push(model.save());
    }
    return _results;
  };

  return ModelContainer;

})();

if ((_ref3 = kohelpers.validate) == null) {
  kohelpers.validate = {};
}

kohelpers.validate.Validator = (function() {

  function Validator(config) {
    var _ref4;
    if (config == null) {
      config = {};
    }
    this.config = config;
    if (config.name) {
      this.name = config.name;
    }
    if ((_ref4 = this.name) == null) {
      this.name = 'Field';
    }
  }

  Validator.prototype.message = function(msg) {
    return this.config.message || msg || this.defaultMessage();
  };

  Validator.prototype.defaultMessage = function() {
    return "Invalid " + (this.name.toLowerCase());
  };

  Validator.prototype.validate = function(value) {
    var deferred,
      _this = this;
    deferred = this.isValid(value);
    if (!(deferred === true || deferred === false)) {
      return deferred;
    }
    return $.Deferred(function(resp) {
      if (deferred === false) {
        resp.resolve(_this.message());
      }
      if (deferred !== false) {
        return resp.resolve();
      }
    });
  };

  Validator.prototype.isValid = function() {
    return true;
  };

  return Validator;

})();

kohelpers.validate.Remote = (function(_super) {

  __extends(Remote, _super);

  function Remote(config) {
    var _ref4;
    Remote.__super__.constructor.call(this, config);
    if (config.field != null) {
      this.field = config.field;
    }
    if (this.field == null) {
      throw 'Field name must be specified';
    }
    if (this.config.url != null) {
      this.url = this.config.url;
    }
    if (!this.url) {
      throw 'Missing server url';
    }
    if (this.config.method != null) {
      this.method = this.config.method;
    }
    if ((_ref4 = this.method) == null) {
      this.method = 'GET';
    }
  }

  Remote.prototype.isValid = function(value) {
    var data, request, response;
    response = $.Deferred();
    data = {};
    data[this.field] = value;
    request = $.ajax(this.url, {
      context: this,
      data: data,
      dataType: 'json',
      type: this.method
    });
    request.done(function() {
      return response.resolve();
    });
    request.error(function(xhr) {
      if (xhr.status === 403 && xhr.responseText) {
        return response.resolve(this.message(xhr.responseText));
      } else {
        return response.resolve(this.message());
      }
    });
    return response;
  };

  return Remote;

})(kohelpers.validate.Validator);

kohelpers.validate.Required = (function(_super) {

  __extends(Required, _super);

  function Required() {
    return Required.__super__.constructor.apply(this, arguments);
  }

  Required.prototype.defaultMessage = function() {
    return "" + this.name + " is required";
  };

  Required.prototype.isValid = function(value) {
    return value !== '' && (value != null);
  };

  return Required;

})(kohelpers.validate.Validator);

kohelpers.validate.Length = (function(_super) {

  __extends(Length, _super);

  function Length(config) {
    if (config == null) {
      config = {};
    }
    Length.__super__.constructor.call(this, config);
    this.length = parseInt(config.length, 10) || 1;
  }

  Length.prototype.defaultMessage = function() {
    return "" + this.name + " must be " + this.length + " characters long";
  };

  Length.prototype.isValid = function(value) {
    var length;
    length = value != null ? value.length : void 0;
    return length >= this.length;
  };

  return Length;

})(kohelpers.validate.Validator);

kohelpers.validate.MinimumLength = (function(_super) {

  __extends(MinimumLength, _super);

  function MinimumLength() {
    return MinimumLength.__super__.constructor.apply(this, arguments);
  }

  MinimumLength.prototype.defaultMessage = function() {
    return "" + this.name + " must be at least " + this.length + " characters";
  };

  MinimumLength.prototype.isValid = function(value) {
    var length;
    length = value != null ? value.length : void 0;
    return length >= this.length;
  };

  return MinimumLength;

})(kohelpers.validate.Length);

kohelpers.validate.MaximumLength = (function(_super) {

  __extends(MaximumLength, _super);

  function MaximumLength() {
    return MaximumLength.__super__.constructor.apply(this, arguments);
  }

  MaximumLength.prototype.defaultMessage = function() {
    return "" + this.name + " cannot be more than " + this.length + " characters";
  };

  MaximumLength.prototype.isValid = function(value) {
    var length;
    length = value != null ? value.length : void 0;
    return length <= this.length;
  };

  return MaximumLength;

})(kohelpers.validate.Length);

kohelpers.validate.Regex = (function(_super) {

  __extends(Regex, _super);

  function Regex(config) {
    if (config == null) {
      config = {};
    }
    Regex.__super__.constructor.call(this, config);
    if (config.pattern) {
      this.pattern = config.pattern;
    }
    if (!this.pattern) {
      throw 'Invalid regex pattern';
    }
  }

  Regex.prototype.isValid = function(value) {
    var length;
    return this.pattern.test(value);
    length = value != null ? value.length : void 0;
    return length <= this.length;
  };

  return Regex;

})(kohelpers.validate.Validator);

kohelpers.validate.Email = (function(_super) {

  __extends(Email, _super);

  function Email() {
    return Email.__super__.constructor.apply(this, arguments);
  }

  Email.prototype.pattern = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$/i;

  return Email;

})(kohelpers.validate.Regex);

kohelpers.validate.PositiveInteger = (function(_super) {

  __extends(PositiveInteger, _super);

  PositiveInteger.prototype.pattern = /^[0-9]+$/;

  function PositiveInteger(config) {
    if (config == null) {
      config = {};
    }
    PositiveInteger.__super__.constructor.call(this, config);
    this.maxValue = config != null ? config.max : void 0;
  }

  PositiveInteger.prototype.value = function(value) {
    return parseInt(value, 10);
  };

  PositiveInteger.prototype.isValid = function(value) {
    var valid;
    valid = PositiveInteger.__super__.isValid.call(this, value);
    if (!this.maxValue && valid) {
      return valid;
    }
    return this.value(value) <= this.maxValue;
  };

  PositiveInteger.prototype.defaultMessage = function() {
    return "" + this.name + " is not a positive integer";
  };

  return PositiveInteger;

})(kohelpers.validate.Regex);

kohelpers.validate.MonthInteger = (function(_super) {

  __extends(MonthInteger, _super);

  function MonthInteger() {
    return MonthInteger.__super__.constructor.apply(this, arguments);
  }

  MonthInteger.prototype.isValid = function(value) {
    var _ref4;
    if (!this.pattern.test(value)) {
      return false;
    }
    return (0 < (_ref4 = this.value(value)) && _ref4 < 13);
  };

  return MonthInteger;

})(kohelpers.validate.PositiveInteger);

kohelpers.validate.DayInteger = (function(_super) {

  __extends(DayInteger, _super);

  function DayInteger(config) {
    this.refMonthField = config.monthField;
    delete config.monthField;
    this.refYearField = config.yearField;
    delete config.yearField;
    DayInteger.__super__.constructor.call(this, config);
  }

  DayInteger.prototype.isValid = function(value) {
    var date, month, year, _ref4;
    if (!this.pattern.test(value)) {
      return false;
    }
    date = new Date();
    month = this.refMonthField();
    year = this.refYearField() || date.getFullYear();
    date = new Date(year, month, 0);
    return (0 < (_ref4 = this.value(value)) && _ref4 <= date.getDate());
  };

  return DayInteger;

})(kohelpers.validate.PositiveInteger);

kohelpers.validate.FutureTimestamp = (function(_super) {

  __extends(FutureTimestamp, _super);

  function FutureTimestamp() {
    return FutureTimestamp.__super__.constructor.apply(this, arguments);
  }

  FutureTimestamp.prototype.isValid = function(value) {
    var date;
    date = new Date();
    date = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    return this.value(value) > date.getTime();
  };

  return FutureTimestamp;

})(kohelpers.validate.PositiveInteger);

kohelpers.validate.YearInteger = (function(_super) {

  __extends(YearInteger, _super);

  function YearInteger() {
    return YearInteger.__super__.constructor.apply(this, arguments);
  }

  YearInteger.prototype.isValid = function(value) {
    var date;
    date = new Date();
    if (!this.pattern.test(value)) {
      return false;
    }
    return date.getFullYear() <= this.value(value);
  };

  return YearInteger;

})(kohelpers.validate.PositiveInteger);

kohelpers.validate.Integer = (function(_super) {

  __extends(Integer, _super);

  function Integer() {
    return Integer.__super__.constructor.apply(this, arguments);
  }

  Integer.prototype.pattern = /^\-?[0-9]+$/;

  Integer.prototype.value = function(value) {
    return parseInt(value, 10);
  };

  Integer.prototype.defaultMessage = function() {
    return "" + this.name + " is not an integer";
  };

  return Integer;

})(kohelpers.validate.Regex);

kohelpers.validate.Equal = (function(_super) {

  __extends(Equal, _super);

  function Equal(config) {
    if (config == null) {
      config = {};
    }
    Equal.__super__.constructor.call(this, config);
    if (config.callback) {
      this.callback = config.callback;
    }
    if (!$.isFunction(this.callback)) {
      throw 'Callback is not a function';
    }
  }

  Equal.prototype.defaultMessage = function() {
    return "" + this.name + " is not equal";
  };

  Equal.prototype.isValid = function(value) {
    return this.callback() === value;
  };

  return Equal;

})(kohelpers.validate.Validator);

kohelpers.validate.NotEqual = (function(_super) {

  __extends(NotEqual, _super);

  function NotEqual() {
    return NotEqual.__super__.constructor.apply(this, arguments);
  }

  NotEqual.prototype.defaultMessage = function() {
    return "" + this.name + " cannot be equal";
  };

  NotEqual.prototype.isValid = function(value) {
    return !NotEqual.__super__.isValid.call(this, value);
  };

  return NotEqual;

})(kohelpers.validate.Equal);

kohelpers.validate.ContainsNumber = (function(_super) {

  __extends(ContainsNumber, _super);

  function ContainsNumber() {
    return ContainsNumber.__super__.constructor.apply(this, arguments);
  }

  ContainsNumber.prototype.pattern = /\d/i;

  ContainsNumber.prototype.defaultMessage = function() {
    return "" + this.name + " must contain a number";
  };

  return ContainsNumber;

})(kohelpers.validate.Regex);

kohelpers.validate.ContainsLowerLetter = (function(_super) {

  __extends(ContainsLowerLetter, _super);

  function ContainsLowerLetter() {
    return ContainsLowerLetter.__super__.constructor.apply(this, arguments);
  }

  ContainsLowerLetter.prototype.pattern = /[a-z]/i;

  ContainsLowerLetter.prototype.defaultMessage = function() {
    return "" + this.name + " must contain a lowercase letter";
  };

  return ContainsLowerLetter;

})(kohelpers.validate.Regex);

kohelpers.validate.AlphaNumeric = (function(_super) {

  __extends(AlphaNumeric, _super);

  function AlphaNumeric() {
    return AlphaNumeric.__super__.constructor.apply(this, arguments);
  }

  AlphaNumeric.prototype.pattern = /^[a-z0-9]+$/i;

  AlphaNumeric.prototype.defaultMessage = function() {
    return "" + this.name + " can only contain numbers and letters";
  };

  return AlphaNumeric;

})(kohelpers.validate.Regex);
