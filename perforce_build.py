import pprint
import os
import shutil
import subprocess
import smtplib, ssl
import json
from P4 import P4, P4Exception
from email.message import EmailMessage

clientTemplate = 'build'
workspaceDir   = 'workspace'
remoteRoot     = 'depot'

# Loads json file specified into python dict
def loadConfig(configFilename):
    configFile = open(configFilename, "r")
    config     = json.loads(configFile.read())
    configFile.close()
    return config

# Login using details specified in config
def perforceLogin(config):
    p4 = P4()
    p4.port     = config["perforcePort"]
    p4.user     = config["perforceUser"]
    p4.password = config["perforcePassword"]
    p4.client   = config["perforceClient"]

    try:
        p4.connect()
        p4.run_login()
    except P4Exception as e:
        print("Error during perforce login:")
        print(e)

    return p4

# Create a local client from template
def setupClient(p4, clientTemplate, workspaceDir):
    # Create a local client from the build template
    client = p4.fetch_client('-t', clientTemplate)
    client['Root'] = f"{os.getcwd()}/{workspaceDir}"
    p4.save_client(client)

    # Create local workspace if it doesn't exist
    if not os.path.exists(workspaceDir):
        os.makedirs(workspaceDir)

def constructFailureNotification(p4, buildResult):
    notificationBody  = "The project build has failed\n\n"
    # Changes since last build
    notificationBody += "Changes since last successful build:\n"
    recentChanges     = getRecentChanges(p4)
    for change in recentChanges:
        notificationBody  += f"{change['change']} - {change['desc']}\n"
        # Basic change contents
        openedFiles        = p4.run_files(f"@={change['change']}")
        for openedFile in openedFiles:
            notificationBody += f"   - {openedFile['depotFile']} : {openedFile['action']}\n"
    # STDOUT / STDERR from build execution
    notificationBody += "STDOUT:\n" + buildResult.stdout.decode("utf-8") + '\n'
    notificationBody += "STDERR:\n" + buildResult.stderr.decode("utf-8") + '\n'

def sendEmail(config, subject, content):
    # Construct msg
    msg            = EmailMessage()
    msg['From']    = config["emailAddress"]
    msg['To']      = ', '.join(config['defaultRecipients'])
    msg['Subject'] = subject
    msg.set_content(str(content))

    # Send via email server
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config["smtpServer"], config["smtpPort"], context=context) as server:
        server.login(config["emailAddress"], config["emailPassword"])
        server.send_message(msg)

# Changes since last submitted in /bin
def getRecentChanges(p4):
    # Lookup last submitted in /bin
    lastBinChange = p4.run_changes("-s", "submitted", "-m", "1", f"//{remoteRoot}/bin/...")[0]
    # List changes since last /bin change
    recentChanges = p4.run_changes(f"//{remoteRoot}/...@>{lastBinChange['change']}")
    return recentChanges    

# p4python passes warnings as an exception
# We need to ensure that 'no file(s) to reconcile' warning doesn't break out script 
def perforceSafeSubmit(p4, reconcilePattern, changeDesc):
    try:
        p4.run_reconcile(reconcilePattern)
        change = p4.fetch_change()
        change._description = changeDesc
        p4.run_submit(change)
    except P4Exception as e:
        # Ignore warning 'no file(s) to reconcile.'
        if 'no file(s) to reconcile' in str(e):
            print(str(e))
            print("No changes to submit")
        else:
            raise(e)


def perforceSubmitBinChanges(p4):
    try:
        p4.run_reconcile(f"//{remoteRoot}/bin/...")
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
        p4 = perforceLogin(config)

        # Setup client
        setupClient(p4, clientTemplate, workspaceDir)

        # Sync workspace with server
        p4.run_sync('-f')

        # Run build
        if (os.name == 'posix'):
            print('Running linux build...')
            buildResult = subprocess.run(["sh", "./build.sh"], cwd=workspaceDir, capture_output=True)
        elif (os.name == 'nt'):
            print('Running windows build...')
            buildResult = subprocess.run(["cmd", "/C", "build.bat"], cwd=workspaceDir, capture_output=True)

        # Check status of build execution
        if(buildResult.returncode != 0):
            print("Build Failure")
            print("Sending notification to default recipients...")
            content = constructFailureNotification(p4, buildResult)
            sendEmail(config, "Build Failure", content)
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
