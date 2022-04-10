from string import Template


def get_repo_query(page: int, pagesize: int, org_name: str):
    index = pagesize * page
    t = Template('''
    {
      organization(login: "$org_name") {
        repositories(orderBy: {direction: DESC, field: PUSHED_AT}, first: $index) {
          pageInfo {
            hasNextPage
            endCursor
          }
          edges {
            node {
              id
              name
              pushedAt
              alertsOpen: vulnerabilityAlerts(states: OPEN) {
                totalCount
              }
              alertsFixed: vulnerabilityAlerts(states: FIXED) {
                totalCount
              }
              alertsDismissed: vulnerabilityAlerts(states: DISMISSED) {
                totalCount
              }
            }
          }
        }
      }
    }
    ''')
    return t.substitute(index=index, org_name=org_name)


def get_alert_query(page: int, pagesize: int, org_name: str, repository_name: str, states: str):
    index = pagesize * page
    t = Template('''
    {
      organization(login: "$org_name") {
        repository(name: "$repository_name") {
          vulnerabilityAlerts(first: $index, states: $states) {
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              createdAt
              dismissedAt
              securityVulnerability {
                package {
                  name
                  ecosystem
                }
                advisory {
                  permalink
                  severity
                  summary
                  identifiers {
                    type
                    value
                  }
                }
              }
            }
          }
        }
      }
    }
    ''')
    return t.substitute(index=index, org_name=org_name, repository_name=repository_name, states=states)
