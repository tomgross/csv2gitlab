import argparse
import csv
import gitlab

# private token authentication


def main():
    parser = argparse.ArgumentParser(description='csv2gitlab - Command line utility to create Gitlab issues from a CSV file')
    parser.add_argument('file',
                    help='The CSV file')
    parser.add_argument('token',
                    help='A token to access gitlab')
    parser.add_argument('--url',
                    help='Gitlab URL',
                    default='https://gitlab.fhnw.ch/')
    parser.add_argument('--project',
                    help='Gitlab project name (i.e. webteam/fhnw.webauftritt)',
                    default='tom.schneider/my_issues')
    args = parser.parse_args()
    gl = gitlab.Gitlab(args.url, args.token)
    project = gl.projects.get(args.project)
    with open(args.file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            data = {'title': row['title'],
                    'description': row['description'],}
            gl.project_issues.create(data, project_id=project.id)

if __name__ == '__main__':
    main()

