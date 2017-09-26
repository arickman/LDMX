#!/usr/bin/env python
import os
import subprocess

def submitJobs(path) :
    fileList = os.listdir(path)
    #for i in range(len(fileList)):
    for i in xrange(0, 10): 
        command = ['bash', '-c', 'source /nfs/slac/g/ldmx/users/arickman/LDMX/setup.sh && env']
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)

        for line in proc.stdout:
            (key, _, value) = line.partition('=')
            os.environ[key] = value.strip()

        for key in os.environ: 
            print 'Key: %s, Value: %s' % (key, os.environ[key])

        proc.communicate()

        print "File: %s" % fileList[i]
        print fileList[i][:-5] + '_results.root'
        

        os.system("bsub python /nfs/slac/g/ldmx/users/arickman/LDMX/ENCounting.py -i /nfs/slac/g/ldmx/production/target_en_output/" + fileList[i])
        
        time.sleep(1)
    

        os.system("bsub python /nfs/slac/g/ldmx/users/arickman/LDMX/ENMom_angle.py -i /nfs/slac/g/ldmx/production/target_en_output/" + fileList[i])
        time.sleep(1)

submitJobs("/nfs/slac/g/ldmx/production/target_en_output/")
