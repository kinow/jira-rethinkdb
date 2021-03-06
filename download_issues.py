#!/usr/bin/env python
config = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.rstrip() #removes trailing whitespace and '\n' chars

        if "=" not in line: continue #skips blanks and comments w/o =
        if line.startswith("#"): continue #skips comments which contain =

        k, v = line.split("=", 1)
        config[k] = v

from jira import JIRA
import rethinkdb as r

def filter_issues(issues):
    filtered = []
    for issue in issues:
        new_issue = {}
        new_issue['key'] = issue.get('key', {})
        new_issue['type'] = issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A')
        new_issue['project_key'] = issue.get('fields', {}).get('project', {}).get('key', 'N/A')
        new_issue['project_name'] = issue.get('fields', {}).get('project', {}).get('name', 'N/A')
        new_issue['fix_versions'] = issue.get('fields', {}).get('fixVersions', [])
        new_issue['resolutiondate'] = issue.get('fields', {}).get('resolutiondate', 'N/A')
        new_issue['created'] = issue.get('fields', {}).get('created', '')
        new_issue['priority'] = issue.get('fields', {}).get('priority', {}).get('name', 'N/A')
        new_issue['labels'] = issue.get('fields', {}).get('labels', [])
        new_issue['assignee_key'] = issue.get('fields', {}).get('assignee', {}).get('key', 'N/A')
        new_issue['assignee_name'] = issue.get('fields', {}).get('assignee', {}).get('displayName', 'N/A')
        new_issue['updated'] = issue.get('fields', {}).get('updated', '')
        new_issue['status'] = issue.get('fields', {}).get('status', {}).get('name', 'N/A')
        new_issue['description'] = issue.get('fields', {}).get('description', 'N/A')
        new_issue['summary'] = issue.get('fields', {}).get('summary', 'N/A')
        new_issue['creator_key'] = issue.get('fields', {}).get('creator', {}).get('key', 'N/A')
        new_issue['creator_name'] = issue.get('fields', {}).get('creator', {}).get('displayName', 'N/A')
        new_issue['subtasks'] = issue.get('fields', {}).get('subtasks', [])

        filtered.append(new_issue)
    return filtered

def main():
    options = {
        'server': config['JIRA']
    }
    jira = JIRA(options, basic_auth=(config['USERNAME'], config['PASSWORD']))

    months = [
        ('2015-03', '2015-04'),
        ('2015-04', '2015-05'),
        ('2015-05', '2015-06'),
        ('2015-06', '2015-07'),
        ('2015-07', '2015-08'),
        ('2015-08', '2015-09'),
        ('2015-09', '2015-10'),
        ('2015-10', '2015-11'),
        ('2015-11', '2015-12'),
        ('2015-12', '2016-01'),
        ('2016-01', '2016-02'),
        ('2016-02', '2016-03'),
        ('2016-03', '2016-04')
    ]

    total_issues = 0
    bulk_add = []
    for month in months:
        print("Downloading issues for interval %s/%s" % month)
        jql = "created >= '%s-01' AND created < '%s-01'" % month
        issues_in_month = jira.search_issues(jql, maxResults=1000, json_result=True)
        issues = issues_in_month['issues']
        
        filtered_issues = filter_issues(issues)
        issues_count = len(issues)
        filtered_count = len(filtered_issues)
        
        assert filtered_count == issues_count

        total_issues = total_issues + issues_count

        bulk_add.extend(filtered_issues)

    print("Successfully downloaded %d issues" % total_issues)
    print("Loading %d issues into RethinkDB" % len(bulk_add))

    r.connect(config['RETHINKDB'], 28015, db='jira').repl()
    r.table_drop('issues').run()
    r.table_create('issues').run()
    r.table('issues').insert(bulk_add).run()

    print("OK! Bye")

if __name__ == '__main__':
    main()