from perforce_build import loadConfig, perforceLogin, setupClient, perforceSafeSubmit
from perforce_build import clientTemplate, workspaceDir, remoteRoot
from P4 import P4, P4Exception

def submitAllChanges(p4, changeDesc):
    perforceSafeSubmit(p4, f"//{remoteRoot}/...", changeDesc)

def goodChange():

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
        f = open(f"{workspaceDir}/src/file1.txt", 'a')
        f.write("This is a good change\n")
        f.close()

        # Reconcile and submit any changes required
        perforceSafeSubmit(p4, f"//{remoteRoot}/src/...", "This change updates src files safely")
        
        # Disconnect
        p4.disconnect()

        print("Valid change submitted")

    except P4Exception as e:
        print(e)

if __name__ == "__main__":
    goodChange()


