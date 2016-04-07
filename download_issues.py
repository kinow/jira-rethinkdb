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

        filtered.append(new_issue)
    return filtered

def main():
    options = {
        'server': config['JIRA']
    }
    jira = JIRA(options, basic_auth=(config['USERNAME'], config['PASSWORD']))

    issues_in_month = jira.search_issues("created >= '2014-03-01' AND created < '2014-04-01'", json_result=True)
    issues = issues_in_month['issues']

    filtered_issues = filter_issues(issues)

    print(filtered_issues)

    # r.connect(RETHINKDB, 28015, db='issues').repl()
    # r.table('issues').insert(issues).run()

if __name__ == '__main__':
    main()