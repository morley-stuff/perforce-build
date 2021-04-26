import os, shutil
from perforce_build import build
from perforce_build import loadConfig, perforceLogin, setupClient, perforceSafeSubmit
from perforce_build import clientTemplate, workspaceDir, remoteRoot
from P4 import P4, P4Exception

def perforce_change(config, change):
    try:
        # Login to perforce with details from config
        p4 = perforceLogin(config)

        # Setup client
        setupClient(p4, clientTemplate, workspaceDir)

        # Sync workspace with server
        p4.run_sync('-f')

        # Perform change and submit
        if (change == 'init'):
            # Delete workspace if it exists
            if os.path.exists(workspaceDir):
                shutil.rmtree(workspaceDir)
            
            # Create workspace with intitial depo state
            shutil.copytree('init_depo', workspaceDir)

            # Reconcile and submit any changes required
            perforceSafeSubmit(p4, f"//{remoteRoot}/...", "Setting to initial state")

            print("Initial depot setup completed")
        
        elif (change == 'good'):
            # Make a change to src files
            f = open(f"{workspaceDir}/src/file1.txt", 'a')
            f.write("This is a good change\n")
            f.close()

            # Reconcile and submit any changes required
            perforceSafeSubmit(p4, f"//{remoteRoot}/src/...", "This change updates src files safely")

            print("Valid change submitted")

        elif (change == 'bad'):
                # Make a change to src files
                os.rename(f"{workspaceDir}/src/file2.txt", f"{workspaceDir}/src/file3.txt")

                # Reconcile and submit any changes required
                perforceSafeSubmit(p4, f"//{remoteRoot}/src/...", "This change introduces an error")

                print("Submitted a change that will break the build")

        elif (change == 'fix'):
            # Make a change to src files
            os.rename(f"{workspaceDir}/src/file3.txt", f"{workspaceDir}/src/file2.txt")

            # Reconcile and submit any changes required
            perforceSafeSubmit(p4, f"//{remoteRoot}/src/...", "This change fixes the error introduced previously")

            print("Submitted a change that will fix the build")

        else:
            print(f"ERROR: Change '{change}' not available")

        p4.disconnect()
    except P4Exception as e:
        print(e)

def testSuite():

    # Load information from config file
    config = loadConfig("config.json")

    print("\n===================\nSETUP\n")
    perforce_change(config, 'init')
    print("\n===================\nBUILD 1\n")
    build()
    print("\n===================\nGOOD CHANGE\n")
    perforce_change(config, 'good')
    print("\n===================\nBUILD 2\n")
    build()
    print("\n===================\nBAD CHANGE\n")
    perforce_change(config, 'bad')
    print("\n===================\nBUILD 3\n")
    build()
    print("\n===================\nFIX CHANGE\n")
    perforce_change(config, 'fix')
    print("\n===================\nBUILD 4\n")
    build()

if __name__ == "__main__":
    testSuite()

