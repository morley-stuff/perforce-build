import os
from perforce_build import loadConfig, perforceLogin, setupClient, perforceSafeSubmit
from perforce_build import clientTemplate, workspaceDir, remoteRoot
from P4 import P4, P4Exception

def fixChange():
    # Load information from config files
    config = loadConfig("config.json")

    try:
        # Login to perforce with details from config
        p4 = perforceLogin(config)

        # Setup client
        setupClient(p4, clientTemplate, workspaceDir)

        # Sync workspace with server
        p4.run_sync('-f')

        # Make a change to src files
        os.rename(f"{workspaceDir}/src/file3.txt", f"{workspaceDir}/src/file2.txt")

        # Reconcile and submit any changes required
        perforceSafeSubmit(p4, f"//{remoteRoot}/src/...", "This change fixes the error introduced previously")
        
        # Disconnect
        p4.disconnect()

        print("Submitted a change that will fix the build")

    except P4Exception as e:
        print(e)

if __name__ == "__main__":
    fixChange()

