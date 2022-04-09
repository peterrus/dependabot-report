# type: ignore
import logging
import os
import argparse
from dataclasses import dataclass, field

import requests
from queries import get_alert_query, get_repo_query

# logging.basicConfig(level=logging.DEBUG)
default_page_size = 100

arg_parser = argparse.ArgumentParser('dependabot-report.py')
arg_parser.add_argument('organisation_name', help='Github organisation name to scan')
args = arg_parser.parse_args()

api_url = 'https://api.github.com/graphql'
headers = {
    'Authorization': 'bearer ' + os.environ.get('GITHUB_TOKEN')
}


@dataclass
class Alert:
    name: str
    # cve_id: str
    # gha_id: str
    # url: str


@dataclass
class Repository:
    name: str
    alerts: list[Alert] = field(default_factory=list)


def get_repos():
    page = 1
    repo_response = None

    while page == 1 or repo_response['data']['organization']['repositories']['pageInfo']['hasNextPage']:
        logging.debug('Doing repo request')
        repo_request = requests.post(
            api_url, headers=headers, json={'query': get_repo_query(page, pagesize=default_page_size, org_name=args.organisation_name)})
        repo_response = repo_request.json()

        for repository_node in repo_response['data']['organization']['repositories']['edges']:
            if repository_node['node']['vulnerabilityAlerts']['totalCount'] > 0:
                yield Repository(name=repository_node['node']['name'])

        page += 1


def get_alerts(repo: Repository):
    page = 1
    alert_response = None

    while page == 1 or alert_response['data']['organization']['repository']['vulnerabilityAlerts']['pageInfo']['hasNextPage']:
        logging.debug(f'Doing alert request for repo {repo.name}')
        alert_request = requests.post(
            api_url, headers=headers, json={'query': get_alert_query(page, pagesize=default_page_size, org_name=args.organisation_name, repository_name=repo.name, states='OPEN')})
        alert_response = alert_request.json()

        for alert_node in alert_response['data']['organization']['repository']['vulnerabilityAlerts']['nodes']:
            yield Alert(name=alert_node['securityVulnerability']['package']['name'])

        page += 1


for repo in get_repos():
    print(f'# Alerts for {repo.name}')
    for alert in get_alerts(repo):
        print(f'  - {alert.name}')
