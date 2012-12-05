kohelpers.form ?= {}

class kohelpers.form.Field

  constructor: (config) ->
    config ?= {}
    @config = config

    @name = config.name if config.name?
    throw 'A field must have a name' unless @name

    if ko.isObservable(config.value)
      @value = config.value
    else
      @value = ko.observable(config.value) if config.value?
      @value = ko.observable(@default) unless config.value?

    @remote = config.remote if config.remote?
    @remote = @name unless @remote?
    @label = config.label if config.label?
    @filter = config.filter
    @default = config.default if config.default?
    @error = ko.observable()
    @errors = ko.observableArray([])
    @errors.subscribe(@onErrors, this)
    @valid = ko.observable()
    @validating = ko.observable()
    @title = ko.computed(@title, this)
    @disabled = ko.observable(false)
    @validators = config.validators ? []
    (validator.name = @label for validator in @validators) if @label

    @value.error = @error
    @value.errors = @errors
    @value.valid = @valid
    @value.validating = @validating
    @value.field = this
    @value.title = @title
    @value.validate = => @validate()
    @value.empty = => @empty()
    @value.reset = (args...) =>
      @reset.apply(this, args)

    @value.subscribe(@onChanged, this)

  title: ->
    return @error() or @label or @name

  validate: (value, validators, deferred) ->
    deferred ?= $.Deferred()

    if arguments.length is 0 and @valid()?
      deferred.resolve(this)
      return deferred

    value ?= @value()
    validators ?= @validators.slice()

    if validators.length < 1
      @validating(false) if @validating()
      @errors([])
      deferred.resolve(this)
      return deferred

    @validating(true) unless @validating()
    validator = validators.shift()
    validator.validate(value).done (error) =>
      if error
        @validating(false) if @validating()
        @errors([error])
        deferred.resolve(this)
      if not error and @validating
        @validate(value, validators, deferred)

    return deferred

  onErrors: (errors) ->
    return if @disabled()
    errors ?= @errors()
    error = errors?[0]
    @error(error)
    @valid(not error?)

  onChanged: (value) ->
    return if @validating() or @disabled()
    value ?= @value()

    if @default? and ((not value?) or value is '')
      @disabled(true)
      value = @default
      @value(@default)
      @disabled(false)

    @validate(value)

  empty: ->
    @reset(undefined)

  reset: (value) ->
    @disabled(true)
    @value(value) unless arguments.length < 1
    @errors([])
    @error(undefined)
    @disabled(false)


class kohelpers.form.Form
  autosave: true
  saveDelay: -1
  responseDelay: -1

  constructor: (config) ->
    config ?= {}
    @config = config
    @fields = []
    @method = config.method or 'POST'

    @autosave = @config.autosave if @config.autosave?
    @saveDelay = @config.saveDelay if @config.saveDelay?
    @responseDelay = @config.responseDelay if @config.responseDelay?

    @submitted = new signals.Signal()
    @saved = new signals.Signal()
    @failed = new signals.Signal()

    @saving = ko.observable(false)
    @processing = ko.observable(false)
    @invalids = ko.observableArray([])
    @invalid = ko.observable()
    @errors = ko.observableArray([])
    @error = ko.observable()

    @invalids.subscribe (invalids) =>
      @invalid(invalids?[0])
      @populateErrors()

    @errors.subscribe (errors) =>
      @error(errors?[0])

    @init(config)

  populateInvalid: ->
    return if @_validating
    invalids = (@[f] for f in @fields when @[f].error())
    @invalids(invalids)

  populateErrors: (invalids) ->
    return if @_validating
    invalids ?= @invalids()
    errors = (i.error() for i in invalids)
    @errors(errors)

  isInvalid: (field) ->
    return @invalid() is @[field] if @[field]?
    return @invalid() is field

  field: (field) ->
    unless field instanceof kohelpers.form.Field
      field = new kohelpers.form.Field(field)

    @fields.push(field.name) unless @fields.indexOf(field.name) > -1

    exists = @[field.name]?
    @[field.name] = field.value unless exists
    @[field.name].error.subscribe(@populateInvalid, this) unless exists
    return @[field.name]

  validate: ->
    return if @_validating
    @_validating = true
    deferred = $.Deferred()
    deferreds = (@[field].validate() for field in @fields)
    $.when.apply($, deferreds).done =>
      @_validating = false
      @populateInvalid()
      deferred.resolve(@invalids().length < 1)
    return deferred

  csrf: ->
    return $('head:first > meta[name=csrf-token]:first').attr('content')

  empty: ->
    @[field].empty() for field in @fields
    return this

  reset: (values) ->
    values ?= {}
    for field in @fields
      hasValue = values.hasOwnProperty(field)
      @[field].reset(values[field]) if hasValue
      @[field].reset() unless hasValue
    return this

  submit: =>
    @validate().done (valid) =>
      return unless valid
      @submitted.dispatch(this)
      @save() if @autosave
    return this

  save: ->
    return this if @saving()
    @saving(true)
    csrf = @csrf()
    headers = {}
    headers['X-CSRFToken'] = csrf if csrf
    endpoint = @endpoint
    data = @todict()
    @processing(true)
    callback = =>
      $.ajax({
        context: this,
        data: JSON.stringify(data),
        mimeType: 'application/json',
        contentType: 'application/json',
        dataType: 'json',
        error: @onError,
        headers: headers,
        success: @onSuccess,
        type: @method,
        url: endpoint
        xhrFields: { withCredentials: true }
      })

    callback() unless @saveDelay > -1
    setTimeout(callback, @saveDelay) if @saveDelay > -1
    return this

  setJsonMimeType: (request) ->
    if request and request.overrideMimeType
      request.overrideMimeType("application/json;charset=UTF-8")


  onSuccess: (value, message, xhr) ->
    callback = =>
      @processing(false)
      @saved.dispatch(this, xhr, value)
      setTimeout((() => @saving(false)), 2)

    callback() if @responseDelay > -1
    setTimeout(callback, @responseDelay) unless @responseDelay > -1

  onError: (xhr, message, value) ->
    callback = =>
      @processing(false)
      txt = 'An error occurred'
      txt = xhr.responseText if xhr.status is 403
      @error(txt)
      @failed.dispatch(this, xhr, value)
      @saving(false)

    callback() unless @responseDelay > -1
    setTimeout(callback, @responseDelay) if @responseDelay > -1

  todict: (args...) ->
    fields = []
    dict = {}

    if args.length < 1
      fields = @fields
    else
      for arg in args
        fields.push(arg) if @fields.indexOf(arg) > -1
      return dict if fields.length < 1

    for field in fields
      continue if @[field].field.filter
      key = @[field].field.remote
      value = @[field]()
      dict[key] = value if value?

    return dict
