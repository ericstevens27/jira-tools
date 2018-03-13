# This program accesses the Graphite version of jira and extracts all of the field names for issues
# It is used to find the jira name for specific fields - such as custom fields - for use in other programs

import getopt, sys
from jira import JIRA
user = 'eric.stevens'

jira_server = 'https://graphitesoftware.atlassian.net'

def usage():
    usageMsg = "This program uses the JIRA Rest API to access and extract issue field names from Jira.\n\
    Usage is:\n\
    python "+sys.argv[0]+" --issue=<string> [options] where options can be:\n\
    \t--issue=<string>: use this issue key (REQUIRED)\n\
    \t--field=<string>: the field description to find.\n\
    \nIf no field description is provided then all fields will be listed.\n\
    If the field has spaces then the string must be enclosed in quotes\n\
    \n\
    \t--help: print this message\n\
    \t--verbose: print messages\n\
    \t--debug: print debug messages\n\
    \n"
    print (usageMsg)

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["help", "verbose", "debug", "issue=", "field="])
except getopt.GetoptError as err:
    # print help information and exit:
    print(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
issueToUse = None
fieldToFind = None
verbose = False
debug = False
for o, a in opts:
    if o in ("--help"):
        usage()
        sys.exit()
    elif o in ("--verbose"):
        verbose = True
    elif o in ("--issue"):
        issueToUse = a
    elif o in ("--field"):
        fieldToFind = a
    elif o in ("--debug"):
        debug = True
    else:
        print ("[ERROR] unknown option {}".format(o))
        usage()
        sys.exit(2)

if issueToUse is None:
    print ("[ERROR] issue is required")
    usage()
    sys.exit(2)

jira = JIRA(server=jira_server, basic_auth=(user, password))

# Fetch all fields
allfields=jira.fields()
# Make a map from field name -> field id
nameMap = {field['name']:field['id'] for field in allfields}
# Fetch an issue
issue = jira.issue(issueToUse)
# You can now look up custom fields by name using the map
if fieldToFind is None:
    for field in allfields:
        print ("{} -> {}".format(field['name'],field['id']))
else:
    print ("{} -> {}".format(fieldToFind,nameMap[fieldToFind]))
