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

### Average time tickets remain open (INcluding currently open)

```
r.db('jira')
  .table('issues')
  .map(function(row) {
    return [r.ISO8601(row('created')), r.branch(row('resolutiondate').eq(null), r.now(), r.ISO8601(row('resolutiondate')))];
  })
  .map(function(row) {
    //return [row(1).sub(row(0)), row(0), row(1)]; 
    return row(1).sub(row(0)); 
  })
  .avg()
```

### Average time tickets remain open (EXcluding currently open)

```
r.db('jira')
  .table('issues')
  .filter(function(row) {
    return row('resolutiondate').eq(null).not()
  })
  .map(function(row) {
    return [r.ISO8601(row('created')), r.branch(row('resolutiondate').eq(null), r.now(), r.ISO8601(row('resolutiondate')))];
  })
  .map(function(row) {
    //return [row(1).sub(row(0)), row(0), row(1)]; 
    return row(1).sub(row(0)); 
  })
  .avg()
```
