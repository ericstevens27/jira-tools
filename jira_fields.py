# This script shows how to use the client in anonymous mode
# against jira.atlassian.com.
from jira import JIRA
user = 'eric.stevens'
password = 'blueCOUGARecho'

# By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK
# (see https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK for details).
# Override this with the options parameter.

jira = JIRA(server='https://graphitesoftware.atlassian.net', basic_auth=(user, password))

proj_to_find = "TPPI"
jql_string = 'project='+proj_to_find+' and assignee=currentUser() ORDER BY key'

# get all issues in project assigned to this user
# all_proj_issues_but_mine = jira.search_issues(jql_string)
# print ("Issue list, assigned to {}".format(user))
# for i in all_proj_issues_but_mine:
#     print (i)

# Fetch all fields
allfields=jira.fields()
# Make a map from field name -> field id
nameMap = {field['name']:field['id'] for field in allfields}
# Fetch an issue
issue = jira.issue('TPPI-10')
# You can now look up custom fields by name using the map
print (issue.fields, nameMap["Resolution"])
print (issue.fields, nameMap["Description"])
print (issue.raw['fields'][nameMap["Description"]])

transitions = jira.transitions(issue)
for t in transitions:
    print (t['id'], t['name'])

# Resolve the issue and assign it to 'pm_user' in one step
jira.transition_issue(issue, 51)
jira.transition_issue(issue, 31)
