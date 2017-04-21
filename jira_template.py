import getopt, sys
from jira import JIRA
import csv

user = 'commander.data'
password = 'Gr1000D1000a_76'
jira_server = 'https://graphitesoftware.atlassian.net'

listSubTask = []
dictSubTask = {
    'project': {'key': ''},
    'summary': 'Test child auto created issue',
    'description': 'Ignore this child. will be deleted shortly',
    'issuetype': {'name': 'Sub-task'},
    'parent': {'id': ''},
}

def usage():
    usageMsg = "This program uses the JIRA Rest API to add template items to selected issues.\n\
    Usage is:\n\
    python "+sys.argv[0]+" [options] where options can be:\n\
    \tOne of:\n\
    \t--project=<string>: use this project key OR\n\
    \t--issue=<issue key>: Add the sub-tasks to this issue only. \n\
    \t--tasks=<file>: holds the subtask templates to use (REQUIRED)\n\
    \n\
    \t--help: print this message\n\
    \t--verbose: print messages\n\
    \t--debug: print debug messages\n\
    \n\
    \tOther Options:\n\
    \t--status=<string>: Use this status in the issue selection when project is used. Default is NEW.\n\
    \n"
    print(usageMsg)


try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["help", "verbose", "debug", "project=", "tasks=", "status=", "issue="])
except getopt.GetoptError as err:
    # print help information and exit:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
project = None
fileTask = None
status='New'
singleIssue = None
verbose = False
debug = False
for o, a in opts:
    if o in ("--help"):
        usage()
        sys.exit()
    elif o in ("--verbose"):
        verbose = True
    elif o in ("--project"):
        project = a
    elif o in ("--tasks"):
        fileTask = a
    elif o in ("--status"):
        status = a
    elif o in ("--issue"):
        singleIssue = a
    elif o in ("--debug"):
        debug = True
    else:
        print("[ERROR] unknown option {}".format(o))
        usage()
        sys.exit(2)

if fileTask is None:
    print("[ERROR] sub task file (--tasks) is required")
    usage()
    sys.exit(2)
if singleIssue is None:
    if project is None:
        print("[ERROR] One of project or issue (--project or --issue) is required")
        usage()
        sys.exit(2)

prevType = ''
with open(fileTask, 'r') as csvfile:
    inputfile = csv.DictReader(csvfile)
    for row in inputfile:
        listSubTask.append([row['ApplyToType'],row['Summary'],row['Description']])

if debug:
    print (listSubTask)

jira = JIRA(server=jira_server, basic_auth=(user, password))
if singleIssue:
    issueToProcess = jira.issue(singleIssue)
    if debug:
        print ('[DEBUG] processing single issue [{}]'.format(singleIssue))
else:
    jql_string = 'project='+project
    jql_string = jql_string + 'AND status=' + status
    jql_string = jql_string+' ORDER BY key'
    if debug:
        print ('[DEBUG] query string is [{}]'.format(jql_string))

allfields=jira.fields()
# Make a map from field name -> field id
nameMap = {field['name']:field['id'] for field in allfields}

listIssuesTouched = []
if singleIssue:
    wType = str(issueToProcess.fields.issuetype)
    if debug:
        print("[DEBUG] processing: {} of type: {}".format(issueToProcess.key, wType))
    for st in listSubTask:
        if debug:
            print("[DEBUG] checking sub type: " + st[1] + " of type: " + st[0])
        if st[0] == wType:
            if debug:
                print("[DEBUG] Yes! Got one!")
            dictSubTask['project']['key'] = 'TPPI'
            dictSubTask['summary'] = st[1]
            dictSubTask['description'] = st[2]
            dictSubTask['parent']['id'] = issueToProcess.key
            child = jira.create_issue(fields=dictSubTask)
            listIssuesTouched.append(issueToProcess.key)
            if verbose:
                print("Created subtask: {} for issue: {}".format(child.key, issueToProcess.key))
else:
    # get all issues in project as per jql string
    issue_list = jira.search_issues(jql_string)
    if debug:
        print ('[DEBUG] issue list is {}'.format(issue_list))
    for i in issue_list:
        wType = str(i.fields.issuetype)
        if debug:
            print ("[DEBUG] processing: {} of type: {}".format(i.key, wType))
        for st in listSubTask:
            if debug:
                print("[DEBUG] checking sub type: " + st[1] + " of type: " + st[0])
            if st[0] == wType:
                if debug:
                    print ("[DEBUG] Yes! Got one!")
                dictSubTask['project']['key'] = 'TPPI'
                dictSubTask['summary'] = st[1]
                dictSubTask['description'] = st[2]
                dictSubTask['parent']['id'] = i.key
                child = jira.create_issue(fields=dictSubTask)
                listIssuesTouched.append(i.key)
                if verbose:
                    print("Created subtask: {} for issue: {}".format(child.key, i.key))

for i in listIssuesTouched:
    comment = jira.add_comment(i, "Added template sub-tasks")

sys.exit(0)