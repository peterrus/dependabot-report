# Dependabot Report

Create a Github Personal Access Token (PAT) with the following scopes: `repo (full), read:org` and place it in `.env` in the following form:

```
GITHUB_TOKEN=yourtoken
```

Then run it with:

```
pipenv install
pipenv run python dependabot-report.py -d -a <YourOrganizationName>
```

Use the `-h` argument to show all available options.
