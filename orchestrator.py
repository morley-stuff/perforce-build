import perforce_build
import perforce_setup,perforce_delete
import perforce_change_good
import perforce_change_bad
import perforce_change_fix

def integrationTest():
    print("\n===================\nDELETE\n")
    perforce_delete.perforceDelete()
    print("\n===================\nSETUP\n")
    perforce_setup.setupPerforce()
    print("\n===================\nBUILD 1\n")
    perforce_build.build()
    print("\n===================\nGOOD CHANGE\n")
    perforce_change_good.goodChange()
    print("\n===================\nBUILD 2\n")
    perforce_build.build()
    print("\n===================\nBAD CHANGE\n")
    perforce_change_bad.badChange()
    print("\n===================\nBUILD 3\n")
    perforce_build.build()
    print("\n===================\nFIX CHANGE\n")
    perforce_change_fix.fixChange()
    print("\n===================\nBUILD 4\n")
    perforce_build.build()


if __name__ == "__main__":
    integrationTest()