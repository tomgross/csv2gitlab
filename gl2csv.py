import argparse
import csv
import gitlab
import pickle

# private token authentication

def enc(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
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
    #issues =  gl.project_issues.list(project_id=25,all=True)
    #pickle.dump(issues, open( "save.p", "wb" ) )
    #print('Saved issues')
    issues = pickle.load(open('save.p', 'rb'))
    fieldnames = ['iid', 'id', 'title', 'state', 'created_at', 'updated_at', 'closed_at']
    f = open('issues.csv', 'w')
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    issue_number = len(issues)
    for i, issue in enumerate(issues):
        print('{:4d}/{:4d}'.format(i, issue_number))
        d = {key: enc(val) for key, val in issue.as_dict().items()
                         if key in fieldnames}
        try:
             notes = issue.notes.list()
        except gitlab.exceptions.GitlabConnectionError:
            print('Can''t get notes for issue {0!s}'.format(issue))
            continue
        if d['state'] == 'closed':
            c = [x.created_at for x in notes if 'closed' in x.body.lower()]
            if c:
                d['closed_at'] = c[0].encode('utf-8')
            else:
                bodys = [x.body.lower() for x in notes if isinstance(x.body, unicode) and 'moved' in x.body.lower()]
                if bodys:
                    continue   # ignore all issues not ment to be here
                else:
                    print('No closing date found {0!s}'.format(issue))
                    print 
                    print(bodys)
                    d['closed_at'] = d['updated_at']
        else:
            d['closed_at'] = ''
        writer.writerow(d)
    f.close()

if __name__ == '__main__':
    main()

