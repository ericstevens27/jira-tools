import getopt, sys
from jira import JIRA
user = 'commander.data'

jira_server = 'https://graphitesoftware.atlassian.net'
defaultQuery = 'project = SER AND Sprint in openSprints() and issuetype in (Story, Bug, Task) ORDER BY assignee DESC, key DESC'

def usage():
    usageMsg = "This program uses the JIRA Rest API to access and extract issue and version data from Jira.\n\
    Usage is:\n\
    python "+sys.argv[0]+" --project=<string> [options] where options can be:\n\
    \t--project=<string>: use this project key (REQUIRED)\n\
    \tOR\n\
    \t--useQuery: use the predefined built in query (REQUIRED)\n\
    \n\
    \t--help: print this message\n\
    \t--verbose: print messages\n\
    \t--debug: print debug messages. Implies verbose\n\
    \t--dryrun: Do not execute the commands, just show the query. Implies verbose and debug\n\
    \n\
    \tUse the following options to select or set variables:\n\
    \t--output=<file>: select the outputfile to use (default is <test.csv>)\n\
    \t--format=<string>: select the format of the output. Valid choices are: csv, html, txt. (default is csv) Note: NOT IMPLEMENTED YET\n\
    \t--version=<string>: use this version identifier (default is all versions in the selected project)\n\
    \t--type=<string>: only items will be of this issue type (default is all types)\n\
    \t--sprint=#: use this sprint number for the query\n\
    \n\
    This program will create a file based on the format selected that contains the issue information for the selected project OR query.\n\
    You must specify the project key to use (--project) or select the --useQuery option. The pre-defined query is: \n\
    \tproject = SER AND Sprint in openSprints() and issuetype in (Story, Bug, Task) ORDER BY assignee DESC, key DESC\n\
    The information extracted is:\n\
    \t* Type\n\
    \t* Key\n\
    \t* Epic\n\
    \t* Status\n\
    \t* Summary\n\
    \t* Project\n\
    \t* Version\n\
    \t* Story Points\n\
    \t* Assignee\n\
    \n"
    print (usageMsg)

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["help", "verbose", "debug", "output=", "project=", "version=", "format=", "type=", "dryrun", "useQuery", "sprint="])
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
dryrun = False
useQuery = False
sprintNumber = 0
for o, a in opts:
    if o in ("--help"):
        usage()
        sys.exit()
    elif o in ("--verbose"):
        verbose = True
    elif o in ("--useQuery"):
        useQuery = True
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
    elif o in ("--sprint"):
        sprintNumber = int(a)
    elif o in ("--debug"):
        debug = True
        verbose = True
    elif o in ("--dryrun"):
        dryrun = True
        debug = True
        verbose = True
    else:
        print ("[ERROR] unknown option {}".format(o))
        usage()
        sys.exit(2)

if project is None:
    if not useQuery:
        print ("[ERROR] project or --useQuery is required")
        usage()
        sys.exit(2)

if verbose:
    print('Using output file: {} with format: {}'.format(output, fmt))
FH = open (output, 'w')

if verbose:
    if useQuery:
        print ('Processing to extract using query: {}'.format(defaultQuery))
    else:
        print ('Processing to extract:\nProject: {}'.format(project))
        if version is None:
            print ('Version: All')
        else:
            print ('Version: {}'.format(version))
        if issuetype is None:
            print ('Issue Type: All')
        else:
            print ('Issue Type: {}'.format(issuetype))
        if sprintNumber == 0:
            print ('Sprint: All')
        else:
            print ('sprint Number: {}'.format(sprintNumber))

# setup stuff you need
jira = JIRA(server=jira_server, basic_auth=(user, password))
assigneePoints = {}
totalPoints = 0

if useQuery:
    jql_string = defaultQuery
else:
    jql_string = 'project='+project
    if version is not None:
        jql_string = jql_string+' and fixVersion="'+version+'"'
    if issuetype is not None:
        jql_string = jql_string+' and issuetype='+issuetype
    if sprintNumber != 0:
        jql_string = jql_string + ' and sprint=' + str(sprintNumber)
    jql_string = jql_string+' ORDER BY key'

# NOTE: after this point jql_string is the only query instructions used
if debug:
        print('[DEBUG] query string is [{}]'.format(jql_string))

if dryrun:
    sys.exit(5)

allfields=jira.fields()
# Make a map from field name -> field id
nameMap = {field['name']:field['id'] for field in allfields}

# get all issues in project as per jql string
issue_list = jira.search_issues(jql_string, maxResults=1000)
if verbose:
    print ("Creating {} records in output file {}, as per [{}]".format(issue_list.total, output, jql_string))
    if issue_list.total > 1000:
        print ('[WARNING] total issues returned is over maximu limit of 1000. Only 1000 issues will be processed.')
FH.write ('"Type","Key","Epic","Status","Summary","Project","Story Points","Assignee"'+"\n")
if debug:
    recCount = 0
for i in issue_list:
    if debug:
        recCount = recCount + 1
        print ('[DEBUG] Processing key [{}]: {}'.format(recCount, i))
    if i.fields.issuetype == "Epic":
        epic_link = None
    else:
        try:
            epic_link = i.raw['fields'][nameMap["Epic Link"]]
        except:
            epic_link = None
    FH.write ('"{}","{}","{}","{}","{}","{}","{}","{}"'.format(i.fields.issuetype, i, epic_link, i.fields.status, i.fields.summary, project, i.fields.customfield_10901, i.fields.assignee)+"\n")
    # count assignee points
    if i.fields.customfield_10901 != None:
        totalPoints = totalPoints + i.fields.customfield_10901
    if i.fields.assignee in assigneePoints:
        if i.fields.customfield_10901 == None:
            assigneePoints[i.fields.assignee] = 0
        else:
            assigneePoints[i.fields.assignee] = assigneePoints[i.fields.assignee] + i.fields.customfield_10901
    else:
        if i.fields.customfield_10901 == None:
            assigneePoints[i.fields.assignee] = 0
        else:
            assigneePoints[i.fields.assignee] = i.fields.customfield_10901

# all done - let's rpint out the assignee list with points
print ('Total points assigned to the sprint: {}'.format(totalPoints))
for k, v in assigneePoints.items():
    print('Assignee: {}: Points: {}'.format(k, v))

FH.close()
sys.exit()
