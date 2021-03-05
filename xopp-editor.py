from hashlib import sha256 
import sys
import os
from XoppFile import XoppFile
import json
import time 

def move(metaData):
    startedThreads=[]
    allPDFFiles=[]
    for (root,dirs,files) in os.walk(metaData["toppath"]):
        for file in files:
            if file.split(".")[-1] == "xopp" and "autosave" not in file:
                with open(f"{root}/{file}","rb") as f:
                    byteContent = f.read()
                    f.close()
                
                sha256sum = sha256(byteContent).hexdigest()
                inData = False

                for metaFile in metaData["files"]:
                    if metaFile["path"] == f'{root}/{file}' and not metaFile["sha256"] == sha256sum:
                        # Start Thread for decompressing and reading of xml
                        startedThreads.append(XoppFile(metaFile,None))
                        inData = True
                    elif metaFile["path"] == f'{root}/{file}' and metaFile["sha256"] == sha256sum:
                        # file not changed  since last run
                        inData = True

                if not inData:
                    # file new 
                    metaFile = {"path":f"{root}/{file}","sha256":"","pdf":""}
                    startedThreads.append(XoppFile(metaFile,None))
            elif file.split(".")[-1] == "pdf":
                allPDFFiles.append(f"{root}/{file}")
    for thread in startedThreads:
        XoppFile.allPDFFiles = allPDFFiles
        thread.start()
    return startedThreads

def setup():
    with open("data.json","r") as f:
        jsonContent = f.read()
    metaData = json.loads(jsonContent)
    threads = move(metaData)
    metaData["files"] = []
    for thread in threads:
        thread.join()
        metaData["files"].append(thread.metaData)
    with open("data.json","w",encoding="utf-8") as f:
        json.dump(metaData,f,ensure_ascii=False)
        f.close()
def mergeFilesFromSameDateinSameFolder(metaData):
    for (root,dirs,files) in os.walk(metaData["toppath"]):
            xoppFiles = []
            dates = []
            for filE in files:
                if filE.split(".")[-1] == "xopp" and "autosave" not in filE:
                    xoppFiles.append(filE)
                    dates.append(filE[:10])
            

            xoppFilesfromDate = []
            datesProcessed = []
            for date in dates:
                if dates.count(date) > 1 and date not in datesProcessed:
                    # more than one file from the same date
                    xoppFilesfromDate = []
                    for xopp in xoppFiles:
                        if date in xopp:
                            xoppFilesfromDate.append(xopp)
                datesProcessed.append(date)
            xoppFilesfromDateMeta = []
            for xoppFileFromDate in xoppFilesfromDate:
                for metaFile in metaData["files"]:
                    if xoppFileFromDate in metaFile["path"]:
                        xoppFilesfromDateMeta.append(metaFile)
            if len(xoppFilesfromDateMeta) > 1:
                rootFile = XoppFile(xoppFilesfromDateMeta[0],"merge")
                for a in range(1,len(xoppFilesfromDateMeta)):
                    # add Files to merge queue
                    rootFile.Mergequeue.append(xoppFilesfromDateMeta[a])
                
                rootFile.start()


                    
if __name__ == '__main__':
    with open("data.json","r") as f:
        jsonContent = f.read()
    metaData = json.loads(jsonContent)
    print(metaData)
    mergeFilesFromSameDateinSameFolder(metaData)