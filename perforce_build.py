import pprint
import os
import shutil
import subprocess
import smtplib, ssl
from sharedfuncs import loadConfig, perforceInit
from P4 import P4, P4Exception
from email.message import EmailMessage

# Notifies email recipients about failure
def sendFailureNotification(config, recentChanges, stdout, stderr):
    # Build email body
    emailBody = "The project build has failed\n\n"
    emailBody = emailBody + "Changes since last successful build:\n"
    for change in recentChanges:
        emailBody += change['change'] + ' - ' + change['desc'] + '\n'
        for openedFile in change['openedFiles']:
            emailBody += "    - " + openedFile['depotFile'] + " : " + openedFile['action'] + "\n"
    emailBody = emailBody + "STDOUT:\n" + stdout + '\n'
    emailBody = emailBody + "STDERR:\n" + stderr + '\n'

    # Construct email
    msg = EmailMessage()
    msg['From']    = config["emailAddress"]
    msg['To']      = ', '.join(config["defaultRecipients"])
    msg['Subject'] = "Build failure"
    msg.set_content(emailBody)

    # Login to smtp server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config["smtpServer"], config["smtpPort"], context=context) as server:
        server.login(config["emailAddress"], config["emailPassword"])
        server.send_message(msg)

# Look up changes since last submitted change in bin dir
def getRecentChanges(p4):
    # Lookup last submitted change in bin directory
    lastBinChange = p4.run_changes("-s", "submitted", "-m", "1", "//depot/bin/...")[0]
    print("Last built at change: ", lastBinChange['change'], '\n')
    # Lookup changes since last submitted build
    recentChanges = p4.run_changes('//depot/...@>' + lastBinChange['change'])
    # Get files opened in each change
    for change in recentChanges:
        openedFiles = p4.run_files('@=' + change['change'])
        change['openedFiles'] = openedFiles

    return recentChanges

def perforceSubmitBinChanges(p4):
    try:
        p4.run_reconcile("//depot/bin/...")
        change = p4.fetch_change()
        change._description = "Project build"
        p4.run_submit(change)
    except P4Exception as e:
        # Warning "No files to reconcile" throws an exception so let's ignore it
        #   and print some nicer output.
        if 'Error' not in str(e):
            print("No changes to submit")
        else:
            raise(e)

def build():
    # Load information from config files
    config = loadConfig("config.json")

    try:
        # Perforce login and initialize workspace
        p4 = perforceInit(config)

        # Get changes since last build
        recentChanges = getRecentChanges(p4)

        # Run build
        if (os.name == 'posix'):
            buildResult = subprocess.run(["sh", "./build.sh"], cwd="root-ws", capture_output=True)
        elif (os.name == 'nt'):
            buildResult = subprocess.run(["cmd", "/C", "build.bat"], cwd="root-ws", capture_output=True)

        pprint.pprint(buildResult)


        # Check status of build execution
        if(buildResult.returncode != 0):
            print("Build Failure")
            print("Sending notification to default recipients...")
            sendFailureNotification(config, recentChanges, buildResult.stdout.decode("utf-8"), buildResult.stderr.decode("utf-8"))
        else:
            # Submit any changes in bin directory
            print("Build Success")
            print("Publishing updated 'binaries'...")
            perforceSubmitBinChanges(p4)
            
        p4.disconnect()
    except P4Exception as e:
        print(e)

if __name__ == "__main__":
    build()
