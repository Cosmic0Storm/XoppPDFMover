from hashlib import sha256 
import sys
import os
from XoppFile import XoppFile
import json
import time 

def scan_for_filechanges(metaData):
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



if __name__ == '__main__':
    with open("data.json","r") as f:
        jsonContent = f.read()
    metaData = json.loads(jsonContent)
    threads = scan_for_filechanges(metaData)
    metaData["files"] = []
    for thread in threads:
        thread.join()
        metaData["files"].append(thread.metaData)
    with open("data.json","w",encoding="utf-8") as f:
        json.dump(metaData,f,ensure_ascii=False)
        f.close()
