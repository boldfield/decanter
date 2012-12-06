DC.admin ?= {}
DC.admin.models ?= {}
DC.admin.forms ?= {}


class DC.Admin extends DC.Application


class DC.AdminNav extends DC.Navigation


class DC.admin.forms.Post extends kohelpers.form.Form


  init: (config) ->

    config ?= {}
    @model = config.model
    @endpoint = "#{DC.app.apiRoot}/post/" unless @model
    @endpoint = "#{DC.app.apiRoot}/post/#{@model.id()}" unless @endpoint

    @field
      name: 'title',
      label: 'Title',
      value: @model?.title or undefined
      validators: [
        new kohelpers.validate.Required(name: 'Title')
      ]

    @field
      name: 'slug',
      label: 'Slug',
      value: @model?.slug or undefined
      validators: [
        new kohelpers.validate.Required(name: 'Slug')
      ]

    @field
      name: 'content',
      label: 'Content',
      value: @model?.content or undefined
      validators: [
        new kohelpers.validate.Required(name: 'Content')
      ]

    @field
      name: 'id',
      value: @model?.id or undefined
      validators: [
      ]

    @field
      name: 'author_id',
      value: @model?.author_id or undefined
      validators: [
      ]

    @title.subscribe(@defaultSlug)

  defaultSlug: =>
    @slug(@title().replace(" ", "-").toLowerCase()) unless @slug()


class DC.admin.models.Post extends kohelpers.model.Model

  @endpoint: (id) ->
    return "#{DC.app.apiRoot}/post/#{id}"

  constructor: (config) ->
    super(config)
    @editLink = ko.computed(@editLink, this)
    @activeFieldName = ko.computed(@activeFieldName, this)

    @endpoint = "#{DC.app.apiRoot}/post/#{@id()}"

  editLink: ->
    return "#{DC.app.adminPath}/posts/edit/#{@id()}"

  activeFieldName: ->
    return "post-#{@id()}-active"


class DC.admin.models.PostContainer extends kohelpers.model.ModelContainer

  model: DC.admin.models.Post

  constructor: (config) ->
    super(config)
    @endpoint = "#{DC.app.apiRoot}/post/"


class DC.admin.models.User extends kohelpers.model.Model

  @endpoint: (username) ->
    return "#{DC.app.apiRoot}/user/#{username}"

  constructor: (config) ->
    super(config)
    @activeFieldName = ko.computed(@activeFieldName, this)

    @endpoint = "#{DC.app.apiRoot}/user/#{@username()}"

    @role_names = ko.computed(@roleNames, this)

  activeFieldName: ->
    return "post-#{@id()}-active"

  roleNames: ->
    rnames = []
    getNames = (role) ->
      rnames.push(role.name())
    @roles().forEach(getNames)
    return rnames.join(',')


class DC.admin.models.UserContainer extends kohelpers.model.ModelContainer

  model: DC.admin.models.User

  constructor: (config) ->
    super(config)
    @endpoint = "#{DC.app.apiRoot}/user/"


class DC.admin.models.Role extends kohelpers.model.Model

  @endpoint: (username) ->
    return "#{DC.app.apiRoot}/role/#{id}"

  constructor: (config) ->
    super(config)
    @endpoint = "#{DC.app.apiRoot}/role/#{@id()}"


class DC.admin.models.RoleContainer extends kohelpers.model.ModelContainer

  model: DC.admin.models.Role

  constructor: (config) ->
    super(config)
    @endpoint = "#{DC.app.apiRoot}/role/"


class DC.admin.PostsPage extends DC.Page

  constructor: (config) ->
    @posts = new DC.admin.models.PostContainer()
    @posts.load()

  newPost: (context, e) ->
    e.preventDefault()
    window.location = "#{DC.app.adminPath}/posts/create"

class DC.admin.UsersPage extends DC.Page

  constructor: (config) ->
    @users = new DC.admin.models.UserContainer()
    @users.load()


class DC.admin.RolesPage extends DC.Page

  constructor: (config) ->
    @groups = new DC.admin.models.RoleContainer()
    @groups.load()


class DC.admin.PostCreatePage extends DC.Page

  constructor: (config) ->
    @form = new DC.admin.forms.Post()
    @form.saved.add(@onSave)

  onSave: =>
    @back()

  cancel: ->
    @back()

  back: ->
    window.location = "#{DC.app.adminPath}/posts"

class DC.admin.PostEditPage extends DC.Page

  constructor: (config) ->
    config ?= {}
    @post = new DC.admin.models.Post({
      id: config.postId,
      author_id: undefined,
      title: undefined,
      slug: undefined,
      content: undefined,
      active: false
    })
    @getPost(config.postId)
    @form = new DC.admin.forms.Post({
      model: @post,
      method: 'PUT'
    })
    @form.saved.add(@onSave)

  getPost: (id) ->
    endpoint = DC.admin.models.Post.endpoint(id)
    headers = {}
    callback = =>
      jQuery.ajax({
        context: this,
        mimeType: 'application/json',
        contentType: 'application/json',
        error: @getPostError,
        headers: headers,
        success: @getPostSuccess,
        type: 'GET',
        url: endpoint
        xhrFields: { withCredentials: true }
      })
    callback()

  getPostSuccess: (xhr, message, value) ->
    data = JSON.parse(value.responseText)
    @post.update(data)

  getPostError: (xhr, message, value) ->

  onSave: =>
    @back()

  cancel: ->
    @back()

  back: ->
    window.location = "#{DC.app.adminPath}/posts"
