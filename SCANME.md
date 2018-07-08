# Infinity

## core.topic
```yaml
fields:
  blockchain:
    '*': ''
  body:
    '*': ''
  categories:
  - '*': ''
  comment_count:
    '*': ''
  created_date:
    '*': ''
  data:
    '*': ''
  editors:
  - '*': ''
  is_draft:
    '*': ''
  languages:
    '*': ''
  owner:
    '*': ''
  parents:
  - '*': ''
  source:
    '*': ''
  title:
    '*': ''
  type:
    '*': ''
  unsubscribed:
  - '*': ''
  updated_date:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## core.comment
```yaml
fields:
  assumed_hours:
    '*': ''
  blockchain:
    '*': ''
  claimed_hours:
    '*': ''
  created_date:
    '*': ''
  data:
    '*': ''
  languages:
    '*': ''
  owner:
    '*': ''
  parent:
    '*': ''
  source:
    '*': ''
  text:
    '*': ''
  topic:
    '*': ''
  updated_date:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## meta.instance
```yaml
fields:
  concept:
    '*': ''
  created_date:
    '*': ''
  data:
    availability:
      '*': ''
    image:
      '*': ''
    price:
      '*': ''
    title:
      '*': ''
    url:
      '*': ''
  description:
    '*': ''
  identifiers:
    '*': ''
  info: {}
  languages:
    '*': ''
  owner:
    '*': ''
  role:
    '*': ''
  schema:
    '*': ''
  source:
    '*': ''
  updated_date:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## meta.schema
```yaml
fields:
  created_date:
    '*': ''
  name:
    '*': ''
  owner:
    '*': ''
  specification:
    _version:
      '*': ''
    availability:
      '*':
        '*': ''
    image:
      '*':
        '*': ''
    image_url:
      '*':
        '*': ''
    price:
      '*':
        '*': ''
    title:
      '*':
        '*': ''
    url:
      '*':
        '*': ''
  types:
  - '*': ''
  updated_date:
    '*': ''
  version:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## meta.type
```yaml
fields:
  created_date:
    '*': ''
  data:
    '*': ''
  definition:
    '*': ''
  is_category:
    '*': ''
  languages:
    '*': ''
  name:
    '*': ''
  parents:
  - '*': ''
  source:
    '*': ''
  updated_date:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## transactions.currency
```yaml
fields:
  created_date:
    '*': ''
  enabled:
    '*': ''
  label:
    '*': ''
  updated_date:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## transactions.currencypricesnapshot
```yaml
fields:
  base:
    '*': ''
  blockchain:
    '*': ''
  blockchain_tx:
    '*': ''
  created_date:
    '*': ''
  data:
    base:
      '*': ''
    date:
      '*': ''
    rates:
      AUD:
        '*': ''
      BGN:
        '*': ''
      BRL:
        '*': ''
      CAD:
        '*': ''
      CHF:
        '*': ''
      CNY:
        '*': ''
      CZK:
        '*': ''
      DKK:
        '*': ''
      GBP:
        '*': ''
      HKD:
        '*': ''
      HRK:
        '*': ''
      HUF:
        '*': ''
      IDR:
        '*': ''
      ILS:
        '*': ''
      INR:
        '*': ''
      JPY:
        '*': ''
      KRW:
        '*': ''
      MXN:
        '*': ''
      MYR:
        '*': ''
      NOK:
        '*': ''
      NZD:
        '*': ''
      PHP:
        '*': ''
      PLN:
        '*': ''
      RON:
        '*': ''
      RUB:
        '*': ''
      SEK:
        '*': ''
      SGD:
        '*': ''
      THB:
        '*': ''
      TRY:
        '*': ''
      USD:
        '*': ''
      ZAR:
        '*': ''
  endpoint:
    '*': ''
  name:
    '*': ''
  updated_date:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## transactions.hourpricesnapshot
```yaml
fields:
  base:
    '*': ''
  blockchain:
    '*': ''
  blockchain_tx:
    '*': ''
  created_date:
    '*': ''
  data:
    count:
      '*': ''
    file_type:
      '*': ''
    limit:
      '*': ''
    observation_end:
      '*': ''
    observation_start:
      '*': ''
    observations:
    - '*': ''
      date:
        '*': ''
      realtime_end:
        '*': ''
      realtime_start:
        '*': ''
      value:
        '*': ''
    offset:
      '*': ''
    order_by:
      '*': ''
    output_type:
      '*': ''
    realtime_end:
      '*': ''
    realtime_start:
      '*': ''
    sort_order:
      '*': ''
    units:
      '*': ''
  endpoint:
    '*': ''
  name:
    '*': ''
  updated_date:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## users.cryptokeypair
```yaml
fields:
  created_date:
    '*': ''
  private_key:
    '*': ''
  public_key:
    '*': ''
  type:
    '*': ''
  updated_date:
    '*': ''
  user:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## users.languagename
```yaml
fields:
  created_date:
    '*': ''
  enabled:
    '*': ''
  lang:
    '*': ''
  name:
    '*': ''
  updated_date:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## users.memberorganization
```yaml
fields:
  created_date:
    '*': ''
  domains:
    '*': ''
  identifiers:
    '*': ''
  updated_date:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## users.onetimepassword
```yaml
fields:
  created_date:
    '*': ''
  is_active:
    '*': ''
  is_used:
    '*': ''
  login_attempts:
    '*': ''
  one_time_password:
    '*': ''
  updated_date:
    '*': ''
  user:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## admin.logentry
```yaml
fields:
  action_flag:
    '*': ''
  action_time:
    '*': ''
  change_message:
    '*': ''
  content_type:
    '*': ''
  object_id:
    '*': ''
  object_repr:
    '*': ''
  user:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## authtoken.token
```yaml
fields:
  created:
    '*': ''
  user:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## captcha.captchastore
```yaml
fields:
  challenge:
    '*': ''
  expiration:
    '*': ''
  hashkey:
    '*': ''
  response:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## contenttypes.contenttype
```yaml
fields:
  app_label:
    '*': ''
  model:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## database.constance
```yaml
fields:
  key:
    '*': ''
  value:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## sessions.session
```yaml
fields:
  expire_date:
    '*': ''
  session_data:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

## sites.site
```yaml
fields:
  domain:
    '*': ''
  name:
    '*': ''
model:
  '*': ''
pk:
  '*': ''
```

