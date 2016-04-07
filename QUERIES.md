## Aggregations

### Issues created per day

```
r.db('jira').table('issues').group(
  r.row('created').slice(0, 10)
).count()
```

### Issues created per month

```
r.db('jira').table('issues').group(
  r.row('created').slice(0, 7)
).count()
```
### Issues created per month with issue type

```
r.db('jira')
  .table('issues')
  .group(
    r.row('created').slice(0, 7), r.row('type')
    )
  .count()
```
