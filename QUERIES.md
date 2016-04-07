## Aggregations

### Issues created per day

```
r.db('jira').table('issues').group(
  r.row('created').slice(0, 10)
).count()
```