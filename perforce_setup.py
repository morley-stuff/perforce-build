import pprint
import os
import shutil
import json
from P4 import P4, P4Exception
from sharedfuncs import loadConfig, perforceInit, perforceLogin

clientTemplateId = 'build'
workspaceDir     = 'workspace'
remoteRoot       = 'depot'

def setupPerforce():

    # Load information from config files
    config = loadConfig("config.json")

    try:
        # Login to perforce with details from config
        p4 = perforceLogin(config)

        # Ensure the build client exists for templating
        try:
            clientTemplate = p4.fetch_client(clientTemplateId)
            clientTemplate['Host'] = ''
            clientTemplate['View'] = f"//{remoteRoot}/... //{clientTemplateId}/..."
            clientTemplate['Options'] = 'allwrite noclobber nocompress unlocked nomodtime normdir'
            p4.save_client(clientTemplate)
        except P4Exception as e:
            print(e)

        # Create a local client from the build template
        client = p4.fetch_client('-t', clientTemplateId)
        client['Root'] = f"{os.getcwd()}/{workspaceDir}"
        p4.save_client(client)

        # Delete workspace if it exists
        if os.path.exists(workspaceDir):
            shutil.rmtree(workspaceDir)
        # Create workspace with intitial depo state
        shutil.copytree('init_depo', workspaceDir)

        # Reconcile and submit any changes required
        p4.run_reconcile(f"//{remoteRoot}/...")
        change = p4.fetch_change()
        change._description = "Setting to initial state"
        p4.run_submit(change)

        # Close perforce connection
        p4.disconnect()

        print("Initial depot setup completed")
    except P4Exception as e:
        print(e)

if __name__ == "__main__":
    setupPerforce()

