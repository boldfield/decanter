kohelpers.model ?= {}


class kohelpers.model.Schema
  constructor: (cls, mapping) ->
    unless jQuery.isFunction(cls)
      mapping = cls
      cls = undefined

    @model = cls
    @mapping = mapping ? {}
    @customFields = []

  addField: (field) ->
    @customFields.push(field)

  key: (key, callback) ->
    if key and callback
      @mapping[key] ?= {}
      @mapping[key].key = callback
    return this

  map: (key, callback) ->
    if key and callback
      @mapping[key] ?= {}
      @mapping[key].create = callback
      @mapping[key].update = callback
    return this

  mapMoment: (keys...) ->
    for key in keys
      @map key, (context) ->
        m = moment(context.data)
        return m if context.observable
        return ko.observable(m)

  mapDependentRemote: (source, target) ->
    @map source, (context) ->
      return context.data if context.observable
      url = context.data
      s = ko.observable(context.data)
      context.parent[target] = context.parent[target] or ko.observable()

      set = (resp) ->
        context.parent[target](resp)

      callback = =>
        jQuery.ajax({
          context: this,
          success: set,
          error: (resp) ->
            console.log('error')
            console.log(resp)
          type: 'GET',
          url: url
          })
      callback()
      return s

  update: (key, callback) ->
    if key and callback
      @mapping[key] ?= {}
      @mapping[key].update = callback
    return this

  addList: (key, args...) ->
    return this unless args.length > 0

    @mapping[key] ?= []

    for arg in args
      if jQuery.isArray(arg)
        arg = arg.slice()
        arg.unshift(key)
        @addList.apply(this, arg)
      else
        @mapping[key].push(arg)

    delete @mapping[key] if @mapping[key].length < 1
    return this

  ignore: (args...) ->
    args.unshift('ignore')
    @addList.apply(this, args)
    return this

  include: (args...) ->
    args.unshift('include')
    @addList.apply(this, args)
    return this

  copy: (args...) ->
    args.unshift('copy')
    @addList.apply(this, args)
    return this

  load: (data, viewModel, onUpdate) ->
    viewModel = @model() if not viewModel and @model

    return ko.mapping.fromJS(data, @mapping) unless viewModel

    ko.mapping.fromJS(data, @mapping, viewModel)
    fields = []
    for f in @customFields
      fields.push(f)
    for k, v of data
      fields.push(k)
    viewModel.fields = fields
    if onUpdate
      for field in fields
        viewModel[field].subscribe(onUpdate) 
    return viewModel

  dump: (viewModel, fields) ->
    filter = (fields) ->
      filtered = {}
      for field in fields
        filtered[field] = viewModel[field]
      return filtered

    data = filter(fields) if fields
    data = viewModel unless data
    return ko.mapping.toJS(data) if data


kohelpers.model.schema = new kohelpers.model.Schema()


class kohelpers.model.Model

  @load: (data) ->
    return new this(data)

  constructor: (data) ->
    @updated = ko.observable(false)
    @schema = @constructor.schema ? kohelpers.model.schema
    @schema.load(data, this, @onValueUpdate)

    @saved = new signals.Signal()
    @failed = new signals.Signal()

    @saving = ko.observable(false)
    @processing = ko.observable(false)

  update: (data) ->
    @schema.load(data, this, @onValueUpdate)
    return this

  dump: ->
    return @schema.dump(this, @fields)

  toJSON: ->
    return ko.toJSON(@schema.dump(this, @fields))

  onValueUpdate: =>
    @updated(true)


  save: ->
    return this if @saving()
    return this if not @updated()
    @saving(true)
    @processing(true)
    headers = {}
    callback = =>
      jQuery.ajax({
        context: this,
        mimeType: 'application/json',
        contentType: 'application/json',
        dataType: 'json',
        data: @toJSON(),
        error: @onError,
        headers: headers,
        success: @onSuccess,
        type: 'PUT',
        url: @endpoint
        xhrFields: { withCredentials: true }
      })

    callback()

    return this

  onError: (xhr, message, value) ->
    callback = =>
      @processing(false)
      @saving(false)
      @failed.dispatch(this, xhr, value)

    callback()

  onSuccess: (value, message, xhr) ->
    callback = =>
      @processing(false)
      @saving(false)
      @saved.dispatch(this, xhr, value)

    callback()


class kohelpers.model.ModelContainer

  @model = undefined
  @endpoint: undefined

  constructor: (config) ->
    config ?= {}
    @config = config

    @loaded = new signals.Signal()
    @failed = new signals.Signal()

    @loading = ko.observable(false)
    @processing = ko.observable(false)

    @models = ko.observableArray([])
    @modelIds = ko.observableArray([])

  load: ->
    return this if @loading()
    @loading(true)
    @processing(true)
    headers = {}
    endpoint = @endpoint
    callback = =>
      jQuery.ajax({
        context: this,
        mimeType: 'application/json',
        contentType: 'application/json',
        error: @onError,
        headers: headers,
        success: @onSuccess,
        type: 'GET'
        url: endpoint
        xhrFields: { withCredentials: true }
      })

    callback()
    return this

  onError: (xhr, message, value) ->
    callback = =>
      @processing(false)
      @failed.dispatch(this, xhr, value)
      @loading(false)
    callback()

  onSuccess: (value, message, xhr) ->
    callback = =>
      @processing(false)
      @loaded.dispatch(this, xhr, value)
      for item in value
        m = new @model(item)
        @models.push(m)

    callback()

  commitUpdated: =>
    for model in @models()
      model.save()
