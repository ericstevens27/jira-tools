import getopt, sys
from jira import JIRA
import csv

user = 'eric.stevens'
password = 'blueCOUGARecho'
jira_server = 'https://graphitesoftware.atlassian.net'


def usage():
    usageMsg = "This program uses the JIRA Rest API to update labels for selected issues.\n\
    Usage is:\n\
    python " + sys.argv[0] + " --input=<file> [options] where options can be:\n\
    \t--input=<file>: use this file as the input file (REQUIRED)\n\
    \n\
    \t--help: print this message\n\
    \t--verbose: print messages\n\
    \t--debug: print debug messages\n\
    \n\
    This program will read a provided file (csv format) and update the issues listed in the file with the labels provided.\n\
    The file must include a header and at least two columns: [IssueKey] and [Label]. Labels will be appended to the existing list\n\
    \n"
    print(usageMsg)


try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["help", "verbose", "debug", "input="])
except getopt.GetoptError as err:
    # print help information and exit:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
inputFile = None
verbose = False
debug = False
for o, a in opts:
    if o in ("--help"):
        usage()
        sys.exit()
    elif o in ("--verbose"):
        verbose = True
    elif o in ("--input"):
        inputFile = a

    elif o in ("--debug"):
        debug = True
    else:
        print("[ERROR] unknown option {}".format(o))
        usage()
        sys.exit(2)

if inputFile is None:
    print("[ERROR] input file (--input) is required")
    usage()
    sys.exit(2)

jira = JIRA(server=jira_server, basic_auth=(user, password))

with open(inputFile, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if debug:
            print(row['IssueKey'], ": ", row['Label'], " : ", row['Recommendation'])

        issue = jira.issue(row['IssueKey'])

        # todo Check that the issue can be modified and have new labels (usually needs ot be an XM issue)

        # modify the List of existing labels. The new label is unicode with no
        # spaces
        if debug:
            print("Current labels are ", issue.fields.labels)
        issue.fields.labels.append(row['Label'])
        if debug:
            print("Labels to be updated are ", issue.fields.labels)
        issue.update(fields={"labels": issue.fields.labels})
        if verbose:
            print(issue.key, " now has labels ", issue.fields.labels)
            if row['Recommendation'] == 'Close':
                print(row['IssueKey'], " <- This issue is marked to be Closed")

f.close()
sys.exit()
