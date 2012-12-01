DC = window.DC = window.DC ? {}


class DC.Application
  log: ->
    console.log('Hello World!')


DC.app = new DC.Application()
DC.app.log()
