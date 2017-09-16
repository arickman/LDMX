#!/usr/bin/env python
import os

def submitJobs(path) :
    fileList = os.listdir(path)
    for i in range(len(fileList)):
        command = ['bash', '-c', 'source /nfs/slac/g/ldmx/users/arickman/LDMX/setup.sh && env']
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)

        for line in proc.stdout:
            (key, _, value) = line.partition('=')
            os.environ[key] = value.strip()

        proc.communicate()

        os.system("bsub python /nfs/slac/g/ldmx/users/arickman/LDMX/ENCounting.py -i /nfs/slac/g/ldmx/production/target_en_output/" + fileList[i])

        command = ['bash', '-c', 'source /nfs/slac/g/ldmx/users/arickman/LDMX/setup.sh && env']
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)

        for line in proc.stdout:
            (key, _, value) = line.partition('=')
            os.environ[key] = value.strip()

        proc.communicate()

        os.system("bsub python /nfs/slac/g/ldmx/users/arickman/LDMX/ENMom_angle.py -i /nfs/slac/g/ldmx/production/target_en_output/" + fileList[i])

submitJobs("/nfs/slac/g/ldmx/production/target_en_output/")
