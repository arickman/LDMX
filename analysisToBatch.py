import os

def submitJobs(path) :
    fileList = os.listdir(path)
    for i in range(len(fileList)):
        print("bsub -q long /nfs/slac/g/ldmx/users/arickman/LDMX/ENCounting.py -i " + fileList[i])
        os.system("bsub -q long /nfs/slac/g/ldmx/users/arickman/LDMX/ENCounting.py -i " + fileList[i])
        os.system("bsub -q long /nfs/slac/g/ldmx/users/arickman/LDMX/ENMom_angle.py -i " + fileList[i])

submitJobs("/nfs/slac/g/ldmx/production/target_en_output/")