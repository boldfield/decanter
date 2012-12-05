DC = window.DC = window.DC ? {}


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

  log: ->
    console.log('Hello World!')


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
