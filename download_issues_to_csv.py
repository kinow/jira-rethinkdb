#!/usr/bin/env python
import os
fileDir  = os.path.dirname(os.path.realpath('__file__'))
OUTPUT = os.path.join(fileDir, 'jira.csv')
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
import csv

def filter_issues(issues):
    filtered = []
    for issue in issues:
        new_issue = {}
        new_issue['key'] = issue.get('key', {})
        new_issue['type'] = issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A')
        new_issue['project_key'] = issue.get('fields', {}).get('project', {}).get('key', 'N/A')
        new_issue['project_name'] = issue.get('fields', {}).get('project', {}).get('name', 'N/A')
        new_issue['fix_versions'] = issue.get('fields', {}).get('fixVersions', [{'name': 'N/A'}])
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
    print("Saving %d issues as CSV" % len(bulk_add))

    with open(OUTPUT, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['key','type','project_key','project_name','fix_version_name','resolutiondate','created','priority','assignee_key','assignee_name','updated','status','summary','creator_key','creator_name','subtasks'])
        for issue in bulk_add:
            fix_version_name = None
            if len(issue['fix_versions']) > 0:
                fix_version_name = issue['fix_versions'][0]['name']
            else:
                fix_version_name = 'N/A'

            description = ''
            if issue['description'] is not None:
                description = issue['description'].encode('utf-8')

            summary = ''
            if issue['summary'] is not None:
                summary = issue['summary'].encode('utf-8')
            row = [
                issue['key'],
                issue['type'],
                issue['project_key'],
                issue['project_name'].encode('utf-8'),
                fix_version_name,
                issue['resolutiondate'],
                issue['created'],
                issue['priority'],
                issue['assignee_key'],
                issue['assignee_name'].encode('utf-8'),
                issue['updated'],
                issue['status'],
                summary,
                issue['creator_key'],
                issue['creator_name'].encode('utf-8'),
                len(issue['subtasks'])
            ]
            try:
                csvwriter.writerow(row)
            except:
                print(row)
                print("Unexpected error:", sys.exc_info()[0])

    print("OK! Bye")

if __name__ == '__main__':
    main()