Requirements
 - python3
 - sh

These python scripts are serve the purpose of testing the build script at perforce_build.py

A fake project is mocked where the build just concats 2 files and stamps it with the current date, pushing it to bin as output.txt

Running orchestrator.py will flow through the full integration test case.
This consists of:
    - Delete everything from perforce depot for a clean slate start
    - Copy the files from resources dir to create standard project layout
    - Perform build (Build should pass and submit build change)
    - Apply a safe change to the project (Just appending some text to one of our src text files)
    - Perform build (Build should pass and submit built change)
    - Apply a breaking change to the project (Rename one of the text files that the build is expecting)
    - Perform build (Build should fail, and send out email notification)
    - Apply a change that fixes the project (Reverses rename)
    - Perform build (Build should pass and submit built change)