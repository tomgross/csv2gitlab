# -*- coding: utf-8 -*-
import sys
import argparse
import csv
import datetime
import gitlab
import iso8601

# private token authentication

def enc(s):
    if isinstance(s, bytes):
        return s.encode('utf-8')
    if isinstance(s, str):
        return s
    elif isinstance(s, int):
        return s
    elif isinstance(s, bool):
        return str(s)
    elif isinstance(s, dict):
        return str(s['name'])
    elif s is None:
        return ''
    elif isinstance(s, list):
        return ','.join([i.encode('utf-8') for i in s])
    else:
        return ''

def main():
    parser = argparse.ArgumentParser(description='gl2csv - Command line utility to export Gitlab issues as CSV file')
    parser.add_argument('token',
                    help='A token to access gitlab')
    parser.add_argument('--url',
                    help='Gitlab URL',
                    default='https://gitlab.fhnw.ch/')
    parser.add_argument('--project',
                    help='Gitlab project name (i.e. webteam/fhnw.webauftritt)',
                    default='webteam/fhnw.webauftritt')
    parser.add_argument('--output',
                    help='Filename to output to',
                    default='issues.csv')

    args = parser.parse_args()
    gl = gitlab.Gitlab(args.url, args.token)
    try:
        project = gl.projects.get(args.project)
        print('Project {} found.'.format(args.project))
    except gitlab.exceptions.GitlabGetError as inst:
        print('Error getting project {0}.'.format(args.project))
        print(inst.args[0])
        sys.exit(-1)

    issues =  project.issues.list(all=True)
    print('{:4d} issues found.'.format(len(issues)))
    
    ###### CONFIGURABLE
    fieldnames = ['iid', 'id', 'title', 'state', 'created_at', 'updated_at', 'closed_at', 'assignee', 'author']
    ######

    f = open(args.output, 'w')
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    issue_number = len(issues)
    all_issues = []
    weeks = {}
    for i, issue in enumerate(issues):
        d = {key: enc(val) for key, val in issue.attributes.items() if key in fieldnames}
        print('{:4d}/{:4d} - ({})'.format(i, issue_number, d))
        try:
             notes = issue.notes.list()
        except gitlab.exceptions.GitlabConnectionError:
            print('Can''t get notes for issue {0!s}'.format(issue))
            continue


        if d['state'] == 'closed':
            c = [x.created_at for x in notes if 'closed' in x.body.lower()]
            if c:
                closed_at = c[0].encode('utf-8')
                d['closed_at'] = closed_at
                closed_date = iso8601.parse_date(closed_at.decode('utf-8'))
            else:
                bodys = [x.body.lower() for x in notes if isinstance(x.body, (str, bytes)) and 'moved' in x.body.lower()]
                if bodys:
                    continue   # ignore all issues not meant to be here
                else:
                    print('No closing date found {0!s}'.format(issue))
                    print 
                    print(bodys)
                    d['closed_at'] = d['updated_at']
                    closed_date = iso8601.parse_date(d['updated_at'].decode('utf-8'))
        else:
            d['closed_at'] = ''
        writer.writerow(d)
    f.close()

if __name__ == '__main__':
    main()

