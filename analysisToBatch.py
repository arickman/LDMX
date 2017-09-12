import os

def submitJobs(path) :
    fileList = os.listdir(path)
    for i in range(len(fileList)):
        os.system("bsub -q medium -o /nfs/slac/g/ldmx/production/arickman/4pt0_gev_e_target_en_v3_magnet /nfs/slac/g/ldmx/users/arickman/LDMX/ENMom_angle.py -i " + fileList[i])
        os.system("bsub -q medium -o /nfs/slac/g/ldmx/production/arickman/4pt0_gev_e_target_en_v3_magnet /nfs/slac/g/ldmx/users/arickman/LDMX/ENMom_angle.py -i " + fileList[i])

submitJobs("/nfs/slac/g/ldmx/production/target_en_output/")
