ko.extenders.validate = (target, opts=[]) ->
  exists = target.validate?
  target.errors ?= ko.observableArray([])
  target.error ?= ko.computed -> target.errors()?[0]
  target.validators ?= []

  for validator in opts
    index = target.validators.indexOf(validator)
    target.validators.push(validator) if index < 0

  target.validate ?= (value) ->
    errors = []
    for v in target.validators
      errors = errors.concat(v.errors(value ? target()))
    target.errors(errors)
    return errors

  target.subscribe(target.validate) unless exists
  return target


ko.extenders.track = (target, enabled) ->
  target.tracking = enabled != false

  target.history ?= ko.observableArray([target()])

  target.previous ?= ko.computed ->
    return target.history()?[0]

  target.dirty ?= ko.computed ->
    return target() is target.history()?[0]

  target.commit ?= ->
    value = target()
    target.history.unshift(target()) if target.history.indexOf(value) != 0
    return target
