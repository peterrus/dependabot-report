# type: ignore
import argparse
import logging
import os

import requests

from classes import Alert, Repository
from markdown import format_alert, format_repo
from queries import get_alert_query, get_repo_query

default_page_size = 100

api_url = 'https://api.github.com/graphql'
headers = {
    'Authorization': 'bearer ' + str(os.environ.get('GITHUB_TOKEN'))
}


def get_alerts(organization_name, repository_name, states='OPEN'):
    page = 1
    alert_response = None

    while page == 1 or alert_response['data']['organization']['repository']['vulnerabilityAlerts']['pageInfo']['hasNextPage']:
        logging.debug(f'Doing alert request for repo {repo.name}')

        alert_json = {'query': get_alert_query(
            page,
            pagesize=default_page_size,
            org_name=organization_name,
            repository_name=repository_name,
            states=states)
        }
        alert_request = requests.post(
            api_url, headers=headers, json=alert_json)

        alert_response = alert_request.json()
        logging.debug(f'Reply from API: {alert_request.text}')

        for alert_node in alert_response['data']['organization']['repository']['vulnerabilityAlerts']['nodes']:
            yield Alert(
                permalink=alert_node['securityVulnerability']['advisory']['permalink'],
                severity=alert_node['securityVulnerability']['advisory']['severity'],
                summary=alert_node['securityVulnerability']['advisory']['summary'],
                package_ecosystem=alert_node['securityVulnerability']['package']['ecosystem'],
                package_name=alert_node['securityVulnerability']['package']['name'],
                identifiers=alert_node['securityVulnerability']['advisory']['identifiers']
            )

        page += 1


def get_repos(organization_name):
    page = 1
    repo_response = None

    while page == 1 or repo_response['data']['organization']['repositories']['pageInfo']['hasNextPage']:
        logging.debug('Doing repo request')
        repo_request = requests.post(
            api_url,
            headers=headers,
            json={'query': get_repo_query(
                page, pagesize=default_page_size, org_name=organization_name)}
        )
        repo_response = repo_request.json()
        logging.debug(f'Reply from API: {repo_request.text}')

        for repository_node in repo_response['data']['organization']['repositories']['edges']:
            yield Repository(
                name=repository_node['node']['name'],
                organization_name=organization_name,
                alerts_open=repository_node['node']['alertsOpen']['totalCount'],
                alerts_fixed=repository_node['node']['alertsFixed']['totalCount'],
                alerts_dismissed=repository_node['node']['alertsDismissed']['totalCount']
            )

        page += 1


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser('dependabot-report.py')
    arg_parser.add_argument('organization_name',
                            help='Github organization name to scan')
    arg_parser.add_argument(
        '-d', dest='show_details', help='Show details for open alerts', action='store_true')
    arg_parser.add_argument(
        '-a', dest='show_all', help='Show all reposities in the organisation with a count of all their alerts', action='store_true')
    arg_parser.add_argument(
        '-v', dest='debug', help='Show debug output', action='store_true')
    args = arg_parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    for repo in get_repos(args.organization_name):
        if args.show_all:
            print(format_repo(repo, full=True))
            if args.show_details:
                print('## Details for open alerts\n')
                for alert in get_alerts(args.organization_name, repo.name, states='OPEN'):
                    print(format_alert(alert) + '\n')
        else:
            if repo.alerts_open > 0:
                print(format_repo(repo, full=False))
                if args.show_details:
                    print('## Details for open alerts\n')
                    for alert in get_alerts(args.organization_name, repo.name, states='OPEN'):
                        print(format_alert(alert) + '\n')
