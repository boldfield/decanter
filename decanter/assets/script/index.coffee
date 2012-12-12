DC = window.DC = window.DC ? {}
DC.models ?= {}


class DC.Application

  @init: (config) ->
    app = DC.app = new this(config)
    return app

  constructor: (config) ->
    config ?= {}
    @protocol = config.protocol
    @protocol = window.location.protocol unless @protocol

    @apiHost = config.apiHost or window.location.host
    @crossDomain = @apiHost != window.location.host if @apiHost
    @crossDomain = false unless @crossDomain

    @apiPathSegment = config.apiPathSegment

    @apiRoot = "#{@protocol}//#{@apiHost}"
    @apiRoot = "#{@apiRoot}/#{@apiPathSegment}" if @apiPathSegment

    @adminPath = config.adminPath or ''
    if @adminPath
      @adminPath = @adminPath.replace('/','')
      @adminPath = "/#{@adminPath}"


class DC.Navigation

  @init: (config) ->
    nav = DC.nav = new this(config)
    return nav

  constructor: (config) ->
    currPath = window.location.pathname
    config ?= {}
    config.targets ?= []
    for target in config.targets
      el = jQuery(target.id)
      item = 
        el: el,
        link: target.link
      @activate(item) if item.link == currPath
      @register(item)
      @[target.id] = item

  activate: (navItem) ->
    navItem.el.parent().addClass('active')

  register: (navItem) ->
    navItem.el.click(@onClick)

  onClick: (e) =>
    e.preventDefault()
    navItem = @["##{e.target.id}"]
    window.location = navItem.link


class DC.Page

  @init: (config) ->
    page = DC.page = new this(config)
    page.render()
    return page

  render: ->
    ko.applyBindings(this)
    return this

  constructor: (config) ->
    config ?= {}

class DC.models.Post extends kohelpers.model.Model

  @schema: post

  @endpoint: (id) ->
    return "#{DC.app.apiRoot}/post/#{id}"

  constructor: (config) ->
    super(config)
    @editLink = ko.computed(@editLink, this)
    @activeFieldName = ko.computed(@activeFieldName, this)

    @endpoint = "#{DC.app.apiRoot}/post/#{@id()}"


post = new kohelpers.model.Schema()
post.addField('content')
post.mapDependentRemote('location', 'content')

class DC.models.PostWithContent extends DC.admin.models.Post

  @schema: post


class DC.models.PostContainer extends kohelpers.model.ModelContainer

  model: DC.models.Post

  constructor: (config) ->
    super(config)
    @endpoint = "#{DC.app.apiRoot}/post/"
