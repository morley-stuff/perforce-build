import os, shutil
from P4 import P4, P4Exception
from perforce_build import loadConfig, perforceLogin, setupClient, perforceSafeSubmit
from perforce_build import clientTemplate, workspaceDir, remoteRoot

clientTemplate = 'build'
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
            template = p4.fetch_client(clientTemplate)
            template['Host'] = ''
            template['View'] = f"//{remoteRoot}/... //{clientTemplate}/..."
            template['Options'] = 'allwrite noclobber nocompress unlocked nomodtime normdir'
            p4.save_client(template)
        except P4Exception as e:
            print(e)

        # Setup client
        setupClient(p4, clientTemplate, workspaceDir)

        # Delete workspace if it exists
        if os.path.exists(workspaceDir):
            shutil.rmtree(workspaceDir)
        # Create workspace with intitial depo state
        shutil.copytree('init_depo', workspaceDir)

        # Reconcile and submit any changes required
        perforceSafeSubmit(p4, f"//{remoteRoot}/...", "Setting to initial state")

        # Close perforce connection
        p4.disconnect()

        print("Initial depot setup completed")
    except P4Exception as e:
        print(e)

if __name__ == "__main__":
    setupPerforce()

