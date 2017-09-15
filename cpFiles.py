#!/usr/bin/env python
import os

def cpFiles(path) :
    fileList = os.listdir(path)
    counter = 0
    while (counter < 100) :
        os.system("cp /nfs/slac/g/ldmx/production/target_en_output/" + fileList[counter] + " /nfs/slac/g/ldmx/users/arickman/LDMX/ENFiles")
        counter += 1

cpFiles("/nfs/slac/g/ldmx/production/target_en_output/")