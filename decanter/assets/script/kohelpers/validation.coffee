kohelpers.validate ?= {}

class kohelpers.validate.Validator

  constructor: (config) ->
    config ?= {}
    @config = config
    @name = config.name if config.name
    @name ?= 'Field'

  message: (msg) ->
    return @config.message or msg or @defaultMessage()

  defaultMessage: ->
    return "Invalid #{@name.toLowerCase()}"

  validate: (value) ->
    deferred = @isValid(value)

    unless deferred is true or deferred is false
      return deferred

    return $.Deferred (resp) =>
      resp.resolve(@message()) if deferred is false
      resp.resolve() unless deferred is false

  isValid: ->
    return true


class kohelpers.validate.Remote extends kohelpers.validate.Validator

  constructor: (config) ->
    super(config)
    @field = config.field if config.field?
    throw 'Field name must be specified' unless @field?

    @url = @config.url if @config.url?
    throw 'Missing server url' unless @url

    @method = @config.method if @config.method?
    @method ?= 'GET'

  isValid: (value) ->
    response = $.Deferred()
    data = {}
    data[@field] = value
    request = $.ajax(@url, {
      context: this,
      data: data,
      dataType: 'json',
      type: @method
    })

    request.done ->
      response.resolve()

    request.error (xhr) ->
      if xhr.status is 403 and xhr.responseText
        response.resolve(@message(xhr.responseText))
      else
        response.resolve(@message())

    return response


class kohelpers.validate.Required extends kohelpers.validate.Validator

  defaultMessage: ->
    return "#{@name} is required"

  isValid: (value) ->
    return value != '' and value?


class kohelpers.validate.Length extends kohelpers.validate.Validator

  constructor: (config) ->
    config ?= {}
    super(config)
    @length = parseInt(config.length, 10) or 1

  defaultMessage: ->
    return "#{@name} must be #{@length} characters long"

  isValid: (value) ->
    length = value?.length
    return length >= @length


class kohelpers.validate.MinimumLength extends kohelpers.validate.Length

  defaultMessage: ->
    return "#{@name} must be at least #{@length} characters"

  isValid: (value) ->
    length = value?.length
    return length >= @length


class kohelpers.validate.MaximumLength extends kohelpers.validate.Length

  defaultMessage: ->
    return "#{@name} cannot be more than #{@length} characters"

  isValid: (value) ->
    length = value?.length
    return length <= @length


class kohelpers.validate.Regex extends kohelpers.validate.Validator

  constructor: (config) ->
    config ?= {}
    super(config)
    @pattern = config.pattern if config.pattern
    throw 'Invalid regex pattern' unless @pattern

  isValid: (value) ->
    return @pattern.test(value)
    length = value?.length
    return length <= @length


class kohelpers.validate.Email extends kohelpers.validate.Regex
  pattern: /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$/i


class kohelpers.validate.PositiveInteger extends kohelpers.validate.Regex
  pattern: /^[0-9]+$/

  constructor: (config) ->
    config ?= {}
    super(config)
    @maxValue = config?.max

  value: (value) ->
    return parseInt(value, 10)

  isValid: (value) ->
    valid = super(value)
    return valid if not @maxValue and valid
    return @value(value) <= @maxValue

  defaultMessage: ->
    return "#{@name} is not a positive integer"


class kohelpers.validate.MonthInteger extends kohelpers.validate.PositiveInteger

  isValid: (value) ->
    return false if not @pattern.test(value)
    return 0 < @value(value) < 13


class kohelpers.validate.DayInteger extends kohelpers.validate.PositiveInteger

  constructor: (config) ->
    @refMonthField = config.monthField
    delete config.monthField
    @refYearField = config.yearField
    delete config.yearField
    super(config)


  isValid: (value) ->
    return false if not @pattern.test(value)
    date = new Date()
    month = @refMonthField()
    year = @refYearField() or date.getFullYear()
    date = new Date(year, month, 0)
    return 0 < @value(value) <= date.getDate()


class kohelpers.validate.FutureTimestamp extends kohelpers.validate.PositiveInteger

  isValid: (value) ->
    date = new Date()
    date = new Date(date.getFullYear(), date.getMonth(), date.getDate())
    return @value(value) > date.getTime()


class kohelpers.validate.YearInteger extends kohelpers.validate.PositiveInteger

  isValid: (value) ->
    date = new Date()
    return false if not @pattern.test(value)
    return date.getFullYear() <= @value(value)


class kohelpers.validate.Integer extends kohelpers.validate.Regex
  pattern: /^\-?[0-9]+$/

  value: (value) ->
    return parseInt(value, 10)

  defaultMessage: ->
    return "#{@name} is not an integer"


class kohelpers.validate.Equal extends kohelpers.validate.Validator

  constructor: (config) ->
    config ?= {}
    super(config)
    @callback = config.callback if config.callback
    throw 'Callback is not a function' unless $.isFunction(@callback)

  defaultMessage: ->
    return "#{@name} is not equal"

  isValid: (value) ->
    return @callback() is value


class kohelpers.validate.NotEqual extends kohelpers.validate.Equal

  defaultMessage: ->
    return "#{@name} cannot be equal"

  isValid: (value) ->
    return not super(value)


class kohelpers.validate.ContainsNumber extends kohelpers.validate.Regex
  pattern: /\d/i

  defaultMessage: ->
    return "#{@name} must contain a number"


class kohelpers.validate.ContainsLowerLetter extends kohelpers.validate.Regex
  pattern: /[a-z]/i

  defaultMessage: ->
    return "#{@name} must contain a lowercase letter"


class kohelpers.validate.AlphaNumeric extends kohelpers.validate.Regex
  pattern: /^[a-z0-9]+$/i

  defaultMessage: ->
    return "#{@name} can only contain numbers and letters"
