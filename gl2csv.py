# -*- coding: utf-8 -*-
import argparse
import csv
import datetime
import gitlab
import pickle
import iso8601
import matplotlib.pyplot as plt
from collections import deque
import numpy

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
    args = parser.parse_args()
    gl = gitlab.Gitlab(args.url, args.token)
    print(args.project)
    project = gl.projects.get(id=25)
    #issues =  project.issues.list(all=True)
    #pickle.dump(issues, open( "save.p", "wb" ) )
    #print('Saved issues')
    issues = pickle.load(open('save.p', 'rb'))
    fieldnames = ['iid', 'id', 'title', 'state', 'created_at', 'updated_at', 'closed_at', 'closed_week']
    f = open('issues.csv', 'w')
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    issue_number = len(issues)
    all_issues = []
    weeks = {}
    for i, issue in enumerate(issues):
        d = {key: enc(val) for key, val in issue.attributes.items()
                         if key in fieldnames}
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
                    continue   # ignore all issues not ment to be here
                else:
                    print('No closing date found {0!s}'.format(issue))
                    print 
                    print(bodys)
                    d['closed_at'] = d['updated_at']
                    closed_date = iso8601.parse_date(d['updated_at'].decode('utf-8'))
            if True:  # closed_date.replace(tzinfo=None) > datetime.datetime(2017,4,1):
                d['closed_week'] = '{:4d}-{:2d}'.format(closed_date.year, closed_date.month)
                # d['closed_week'] = '{:4d}-{:2d}'.format(*closed_date.isocalendar()[:2])
            else:
                d['closed_week'] = ''
        else:
            d['closed_at'] = ''
            d['closed_week'] = ''
        #writer.writerow(d)
        all_issues.append(d)
        if d['closed_week']:
            if d['closed_week'] not in weeks:
                weeks[d['closed_week']] = 0
            weeks[d['closed_week']] += 1
    issues_count = list(weeks.values())
    print(weeks)
    print('Minimum gelöst: {0} '.format(min([x for x in issues_count if x])))
    print('Maximum gelöst: {0} '.format(max(issues_count)))
    print('Median: {0} '.format(numpy.median(issues_count)))
    print('Mittelwert: {0} '.format(numpy.average(issues_count)))
    # 17 is because we started at week #36 in 2016
    # 15 are the zero weeks  19.5.2017
    wX = weeks.keys()
    wY = issues_count
    plt.plot(wX, wY)
    plt.xlabel(u'Monat')
    plt.ylabel(u'gelöste Issues')
    plt.show()
    #f.close()

if __name__ == '__main__':
    main()

