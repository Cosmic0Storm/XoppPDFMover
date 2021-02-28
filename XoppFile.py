import gzip
import xml.etree.ElementTree as ET
from threading import Thread
from subprocess import call
from os import path
from hashlib import sha256


class XoppFile(Thread):

    allPDFFiles = []


    def __init__(self,metaData,allPDFFiles):
        # metaData : dir {"filepath":"pathtofile","sha256":"sha256sum of file","pdfassigned","pathtofile"}
        Thread.__init__(self)
        self.metaData=metaData
        self.usedPDFFile = None     

    def findPDFFilebyName(self,filename):
        if filename != "" or filename.split(".")[-1]=="pdf":
            for pdf in XoppFile.allPDFFiles:
                if filename in pdf:
                    return pdf


    def moveBackgroundPdf(self):
        #print(self.metaData)
        #print(self.allPDFFiles)
        with gzip.open(self.metaData["path"],"rb") as f:
            filecontent = f.read()
            f.close()

        xmlRoot = ET.fromstring(filecontent)

        changesHappend = False

        for child in xmlRoot:
            for background in child.iter("background"):
                if background.attrib["type"] == "pdf" and "filename" in background.attrib.keys():
                    if not path.exists(background.attrib['filename']):
                        #print(background.attrib['filename'].split("/")[-1])
                        sourcePath = self.findPDFFilebyName(background.attrib['filename'].split('/')[-1])
                        
                    else:
                        sourcePath = background.attrib['filename']
                    destPath = f"{path.dirname(self.metaData['path'])}/.{background.attrib['filename'].split('/')[-1]}"
                    print(f"{background.attrib['filename'].split('/')[-1]},{sourcePath}=>{destPath},{self.metaData['path']}")
                    if sourcePath is not None and destPath is not None:
                        call(["cp",sourcePath,destPath])
                    self.usedPDFFile=sourcePath
                    background.set('filename',destPath)
                    background.set('domain','attach')
                    changesHappend = True
        if changesHappend:
            xmlstr = ET.tostring(xmlRoot,encoding='utf-8',method='xml')
            gzXml = gzip.compress(xmlstr)

            self.metaData["sha256"] = sha256(gzXml).hexdigest()
            self.metaData["pdf"] = destPath
            with open(self.metaData["path"],"wb") as f:
                f.write(gzXml)
                f.close()
        else:
            with open(self.metaData["path"],"rb") as f:
                self.metaData["sha256"] = sha256(f.read()).hexdigest()
            f.close()

        


    def run(self):
        try:
            self.moveBackgroundPdf()
        except ET.ParseError as e:
            print(self.metaData)