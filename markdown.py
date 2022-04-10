from string import Template
from textwrap import dedent

from classes import Alert, Repository


def format_alert(alert: Alert):
    t = Template(dedent('''\
    **$severity: $package_name ($package_ecosystem)**
    $summary

    [View on Github]($permalink)
    Identifiers: $identifiers'''))

    template_vars = alert.__dict__
    template_vars['identifiers'] = ', '.join(
        [f"{i['type']}: {i['value']}" for i in alert.identifiers])

    return t.substitute(alert.__dict__)


def format_repo(repo: Repository, full=False):
    if full:
        t = Template(dedent('''\
        # $name

        - **Open:**\t\t\t$alerts_open
        - **Fixed:**\t\t$alerts_fixed
        - **Dismissed:**\t$alerts_dismissed
        '''))
        return t.substitute(repo.__dict__)
    else:
        t = Template(dedent('''\
        # $name
        - **Open:**\t\t\t$alerts_open
        '''))
        return t.substitute(repo.__dict__)
