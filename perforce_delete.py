from perforce_build import loadConfig, perforceLogin, setupClient, perforceSafeSubmit
from perforce_build import clientTemplate, workspaceDir, remoteRoot
from P4 import P4, P4Exception

def perforceDelete():
# Load information from config files
    config = loadConfig("config.json")

    try:
        # Perforce login and initialize workspace
        p4 = perforceInit(config)

        # Delete everything
        p4.run_delete(f"//{remoteRoot}/...")
        change = p4.fetch_change()
        change._description = "This change deletes everything in the depot"
        p4.run_submit(change)
        
        print("All files deleted from depot")

        p4.disconnect()

    except P4Exception as e:
        print(e)

    if os.path.exists(remoteRoot):
        shutil.rmtree(remoteRoot)

if __name__ == "__main__":
    perforceDelete()