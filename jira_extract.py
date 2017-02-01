import getopt, sys
from jira import JIRA
user = 'eric.stevens'
password = 'blueCOUGARecho'
jira_server = 'https://graphitesoftware.atlassian.net'

def usage():
    usageMsg = "This program uses the JIRA Rest API to access and extract issue and version data from Jira.\n\
    Usage is:\n\
    python "+sys.argv[0]+" --project=<string> [options] where options can be:\n\
    \t--project=<string>: use this project key (REQUIRED)\n\
    \n\
    \t--help: print this message\n\
    \t--verbose: print messages\n\
    \t--debug: print debug messages\n\
    \n\
    \tUse the following options to select or set variables:\n\
    \t--output=<file>: select the outputfile to use (default is <test.csv>)\n\
    \t--format=<string>: select the format of the output. Valid choices are: csv, html, txt. (default is csv) Note: NOT IMPLEMENTED YET\n\
    \t--version=<string>: use this version identifier (default is all versions in the selected project)\n\
    \t--type=<string>: only items will be of this issue type (default is all types)\n\
    \n\
    This program will create a file based on the format selected that contains the issue information for the selected project.\n\
    You must specify the project key to use (--project). \n\
    The information extracted is:\n\
    \t* field list\n\
    \n"
    print (usageMsg)

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["help", "verbose", "debug", "output=", "project=", "version=", "format=", "type="])
except getopt.GetoptError as err:
    # print help information and exit:
    print(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
output = "test.csv"
fmt = 'csv'
project = None
version = None
issuetype = None
verbose = False
debug = False
for o, a in opts:
    if o in ("--help"):
        usage()
        sys.exit()
    elif o in ("--verbose"):
        verbose = True
    elif o in ("--output"):
        output = a
    elif o in ("--project"):
        project = a
    elif o in ("--format"):
        fmt = a
    elif o in ("--version"):
        version = a
    elif o in ("--type"):
        issuetype = a
    elif o in ("--debug"):
        debug = True
    else:
        print ("[ERROR] unknown option {}".format(o))
        usage()
        sys.ext(2)

if project is None:
    print ("[ERROR] project is required")
    usage()
    sys.ext(2)

if verbose:
    print('Using output file: {} with format: {}'.format(output, fmt))
FH = open (output, 'w')

if verbose:
    print ('Processing to extract:\nProject: {}'.format(project))
    if version is None:
        print ('Version: All')
    else:
        print ('Version: {}'.format(version))
    if issuetype is None:
        print ('Issue Type: All')
    else:
        print ('Issue Type: {}'.format(issuetype))

jira = JIRA(server=jira_server, basic_auth=(user, password))

jql_string = 'project='+project
if version is not None:
    jql_string = jql_string+' and fixVersion='+version
if issuetype is not None:
    jql_string = jql_string+' and issuetype='+issuetype
jql_string = jql_string+' ORDER BY key'

if debug:
    print ('[DEBUG] query string is [{}]'.format(jql_string))

allfields=jira.fields()
# Make a map from field name -> field id
nameMap = {field['name']:field['id'] for field in allfields}

# get all issues in project as per jql string
issue_list = jira.search_issues(jql_string)
print ("Issue list, as per [{}]".format(jql_string))
FH.write ('"Type","Key","Epic","Status","Summary","Project","Version","Version Start Date","Version Release Date"'+"\n")
for i in issue_list:
    if i.fields.issuetype == "Epic":
        epic_link = None
    else:
        try:
            epic_link = i.raw['fields'][nameMap["Epic Link"]]
        except:
            epic_link = None
    for j in i.fields.fixVersions:
        v = jira.version(j.id)
        try:
            relDate = v.releaseDate
        except:
            relDate = None
        try:
            sDate = v.startDate
        except:
            sDate = None
        FH.write ('"{}","{}","{}","{}","{}","{}","{}","{}","{}"'.format(i.fields.issuetype, i, epic_link, i.fields.status, i.fields.summary, project, v.name, sDate, relDate)+"\n")

FH.close()
sys.exit()
