var DC, _base, _base1, _ref, _ref1, _ref2, _ref3,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

DC = window.DC = (_ref = window.DC) != null ? _ref : {};

DC.Application = (function() {

  Application.init = function(config) {
    var app;
    app = DC.app = new this(config);
    return app;
  };

  function Application(config) {
    if (config == null) {
      config = {};
    }
    this.protocol = config.protocol;
    if (!this.protocol) {
      this.protocol = window.location.protocol;
    }
    this.apiHost = config.apiHost || window.location.host;
    if (this.apiHost) {
      this.crossDomain = this.apiHost !== window.location.host;
    }
    if (!this.crossDomain) {
      this.crossDomain = false;
    }
    this.apiPathSegment = config.apiPathSegment;
    this.apiRoot = "" + this.protocol + "//" + this.apiHost;
    if (this.apiPathSegment) {
      this.apiRoot = "" + this.apiRoot + "/" + this.apiPathSegment;
    }
    this.adminPath = config.adminPath || '';
    if (this.adminPath) {
      this.adminPath = this.adminPath.replace('/', '');
      this.adminPath = "/" + this.adminPath;
    }
  }

  return Application;

})();

DC.Navigation = (function() {

  Navigation.init = function(config) {
    var nav;
    nav = DC.nav = new this(config);
    return nav;
  };

  function Navigation(config) {
    this.onClick = __bind(this.onClick, this);

    var currPath, el, item, target, _i, _len, _ref1, _ref2;
    currPath = window.location.pathname;
    if (config == null) {
      config = {};
    }
    if ((_ref1 = config.targets) == null) {
      config.targets = [];
    }
    _ref2 = config.targets;
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      target = _ref2[_i];
      el = jQuery(target.id);
      item = {
        el: el,
        link: target.link
      };
      if (item.link === currPath) {
        this.activate(item);
      }
      this.register(item);
      this[target.id] = item;
    }
  }

  Navigation.prototype.activate = function(navItem) {
    return navItem.el.parent().addClass('active');
  };

  Navigation.prototype.register = function(navItem) {
    return navItem.el.click(this.onClick);
  };

  Navigation.prototype.onClick = function(e) {
    var navItem;
    e.preventDefault();
    navItem = this["#" + e.target.id];
    return window.location = navItem.link;
  };

  return Navigation;

})();

DC.Page = (function() {

  Page.init = function(config) {
    var page;
    page = DC.page = new this(config);
    page.render();
    return page;
  };

  Page.prototype.render = function() {
    ko.applyBindings(this);
    return this;
  };

  function Page(config) {
    if (config == null) {
      config = {};
    }
  }

  return Page;

})();

if ((_ref1 = DC.admin) == null) {
  DC.admin = {};
}

if ((_ref2 = (_base = DC.admin).models) == null) {
  _base.models = {};
}

if ((_ref3 = (_base1 = DC.admin).forms) == null) {
  _base1.forms = {};
}

DC.Admin = (function(_super) {

  __extends(Admin, _super);

  function Admin() {
    return Admin.__super__.constructor.apply(this, arguments);
  }

  return Admin;

})(DC.Application);

DC.AdminNav = (function(_super) {

  __extends(AdminNav, _super);

  function AdminNav() {
    this.onClick = __bind(this.onClick, this);
    return AdminNav.__super__.constructor.apply(this, arguments);
  }

  AdminNav.prototype.onClick = function(e) {
    var navItem;
    e.preventDefault();
    navItem = this["#" + e.target.id];
    return window.location = "" + DC.app.adminPath + navItem.link;
  };

  return AdminNav;

})(DC.Navigation);

DC.admin.forms.Post = (function(_super) {

  __extends(Post, _super);

  function Post() {
    this.defaultSlug = __bind(this.defaultSlug, this);
    return Post.__super__.constructor.apply(this, arguments);
  }

  Post.prototype.init = function(config) {
    var _ref4, _ref5, _ref6, _ref7, _ref8;
    if (config == null) {
      config = {};
    }
    this.model = config.model;
    if (!this.model) {
      this.endpoint = "" + DC.app.apiRoot + "/post/";
    }
    if (!this.endpoint) {
      this.endpoint = "" + DC.app.apiRoot + "/post/" + (this.model.id());
    }
    this.field({
      name: 'title',
      label: 'Title',
      value: ((_ref4 = this.model) != null ? _ref4.title : void 0) || void 0,
      validators: [
        new kohelpers.validate.Required({
          name: 'Title'
        })
      ]
    });
    this.field({
      name: 'slug',
      label: 'Slug',
      value: ((_ref5 = this.model) != null ? _ref5.slug : void 0) || void 0,
      validators: [
        new kohelpers.validate.Required({
          name: 'Slug'
        })
      ]
    });
    this.field({
      name: 'content',
      label: 'Content',
      value: ((_ref6 = this.model) != null ? _ref6.content : void 0) || void 0,
      validators: [
        new kohelpers.validate.Required({
          name: 'Content'
        })
      ]
    });
    this.field({
      name: 'id',
      value: ((_ref7 = this.model) != null ? _ref7.id : void 0) || void 0,
      validators: []
    });
    this.field({
      name: 'author_id',
      value: ((_ref8 = this.model) != null ? _ref8.author_id : void 0) || void 0,
      validators: []
    });
    return this.title.subscribe(this.defaultSlug);
  };

  Post.prototype.defaultSlug = function() {
    if (!this.slug()) {
      return this.slug(this.title().replace(" ", "-").toLowerCase());
    }
  };

  return Post;

})(kohelpers.form.Form);

DC.admin.models.Post = (function(_super) {

  __extends(Post, _super);

  Post.endpoint = function(id) {
    return "" + DC.app.apiRoot + "/post/" + id;
  };

  function Post(config) {
    Post.__super__.constructor.call(this, config);
    this.editLink = ko.computed(this.editLink, this);
    this.activeFieldName = ko.computed(this.activeFieldName, this);
    this.endpoint = "" + DC.app.apiRoot + "/post/" + (this.id());
  }

  Post.prototype.editLink = function() {
    return "" + DC.app.adminPath + "/posts/edit/" + (this.id());
  };

  Post.prototype.activeFieldName = function() {
    return "post-" + (this.id()) + "-active";
  };

  return Post;

})(kohelpers.model.Model);

DC.admin.models.PostContainer = (function(_super) {

  __extends(PostContainer, _super);

  PostContainer.prototype.model = DC.admin.models.Post;

  function PostContainer(config) {
    PostContainer.__super__.constructor.call(this, config);
    this.endpoint = "" + DC.app.apiRoot + "/post/";
  }

  return PostContainer;

})(kohelpers.model.ModelContainer);

DC.admin.models.User = (function(_super) {

  __extends(User, _super);

  User.endpoint = function(username) {
    return "" + DC.app.apiRoot + "/user/" + username;
  };

  function User(config) {
    User.__super__.constructor.call(this, config);
    this.activeFieldName = ko.computed(this.activeFieldName, this);
    this.endpoint = "" + DC.app.apiRoot + "/user/" + (this.username());
    this.role_names = ko.computed(this.roleNames, this);
  }

  User.prototype.activeFieldName = function() {
    return "post-" + (this.id()) + "-active";
  };

  User.prototype.roleNames = function() {
    var getNames, rnames;
    rnames = [];
    getNames = function(role) {
      return rnames.push(role.name());
    };
    this.roles().forEach(getNames);
    return rnames.join(',');
  };

  return User;

})(kohelpers.model.Model);

DC.admin.models.UserContainer = (function(_super) {

  __extends(UserContainer, _super);

  UserContainer.prototype.model = DC.admin.models.User;

  function UserContainer(config) {
    UserContainer.__super__.constructor.call(this, config);
    this.endpoint = "" + DC.app.apiRoot + "/user/";
  }

  return UserContainer;

})(kohelpers.model.ModelContainer);

DC.admin.models.Role = (function(_super) {

  __extends(Role, _super);

  Role.endpoint = function(username) {
    return "" + DC.app.apiRoot + "/role/" + id;
  };

  function Role(config) {
    Role.__super__.constructor.call(this, config);
    this.endpoint = "" + DC.app.apiRoot + "/role/" + (this.id());
  }

  return Role;

})(kohelpers.model.Model);

DC.admin.models.RoleContainer = (function(_super) {

  __extends(RoleContainer, _super);

  RoleContainer.prototype.model = DC.admin.models.Role;

  function RoleContainer(config) {
    RoleContainer.__super__.constructor.call(this, config);
    this.endpoint = "" + DC.app.apiRoot + "/role/";
  }

  return RoleContainer;

})(kohelpers.model.ModelContainer);

DC.admin.PostsPage = (function(_super) {

  __extends(PostsPage, _super);

  function PostsPage(config) {
    this.posts = new DC.admin.models.PostContainer();
    this.posts.load();
  }

  PostsPage.prototype.newPost = function(context, e) {
    e.preventDefault();
    return window.location = "" + DC.app.adminPath + "/posts/create";
  };

  return PostsPage;

})(DC.Page);

DC.admin.UsersPage = (function(_super) {

  __extends(UsersPage, _super);

  function UsersPage(config) {
    this.users = new DC.admin.models.UserContainer();
    this.users.load();
  }

  return UsersPage;

})(DC.Page);

DC.admin.RolesPage = (function(_super) {

  __extends(RolesPage, _super);

  function RolesPage(config) {
    this.groups = new DC.admin.models.RoleContainer();
    this.groups.load();
  }

  return RolesPage;

})(DC.Page);

DC.admin.PostCreatePage = (function(_super) {

  __extends(PostCreatePage, _super);

  function PostCreatePage(config) {
    this.onSave = __bind(this.onSave, this);
    this.form = new DC.admin.forms.Post();
    this.form.saved.add(this.onSave);
  }

  PostCreatePage.prototype.onSave = function() {
    return this.back();
  };

  PostCreatePage.prototype.cancel = function() {
    return this.back();
  };

  PostCreatePage.prototype.back = function() {
    return window.location = "" + DC.app.adminPath + "/posts";
  };

  return PostCreatePage;

})(DC.Page);

DC.admin.PostEditPage = (function(_super) {

  __extends(PostEditPage, _super);

  function PostEditPage(config) {
    this.onSave = __bind(this.onSave, this);
    if (config == null) {
      config = {};
    }
    this.post = new DC.admin.models.Post({
      id: config.postId,
      author_id: void 0,
      title: void 0,
      slug: void 0,
      content: void 0,
      active: false
    });
    this.getPost(config.postId);
    this.form = new DC.admin.forms.Post({
      model: this.post,
      method: 'PUT'
    });
    this.form.saved.add(this.onSave);
  }

  PostEditPage.prototype.getPost = function(id) {
    var callback, endpoint, headers,
      _this = this;
    endpoint = DC.admin.models.Post.endpoint(id);
    headers = {};
    callback = function() {
      return jQuery.ajax({
        context: _this,
        mimeType: 'application/json',
        contentType: 'application/json',
        error: _this.getPostError,
        headers: headers,
        success: _this.getPostSuccess,
        type: 'GET',
        url: endpoint,
        xhrFields: {
          withCredentials: true
        }
      });
    };
    return callback();
  };

  PostEditPage.prototype.getPostSuccess = function(xhr, message, value) {
    var data;
    data = JSON.parse(value.responseText);
    return this.post.update(data);
  };

  PostEditPage.prototype.getPostError = function(xhr, message, value) {};

  PostEditPage.prototype.onSave = function() {
    return this.back();
  };

  PostEditPage.prototype.cancel = function() {
    return this.back();
  };

  PostEditPage.prototype.back = function() {
    return window.location = "" + DC.app.adminPath + "/posts";
  };

  return PostEditPage;

})(DC.Page);
