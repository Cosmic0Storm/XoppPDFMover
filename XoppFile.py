import gzip
import xml.etree.ElementTree as ET
from threading import Thread
from subprocess import call
from os import path
from hashlib import sha256


class XoppFile(Thread):

    allPDFFiles = []


    def __init__(self,metaData,args):
        # metaData : dir {"path":"path/to/file","sha256":"sha256sum of file","pdf","pathtofile"}
        Thread.__init__(self)
        self.metaData=metaData
        self.args = args
        self.usedPDFFile = None     
        self.Mergequeue = []

    def findPDFFilebyName(self,filename):
        if filename != "" or filename.split(".")[-1]=="pdf":
            for pdf in XoppFile.allPDFFiles:
                if filename in pdf:
                    return pdf


    def moveBackgroundPdf(self):
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

    def mergeWithFile(self,metaData):
        if metaData["pdf"] != self.metaData["pdf"] and metaData["pdf"] != "":
            return
        
        with gzip.open(self.metaData["path"],"rb") as f:
            file1 = f.read()
            f.close()

        with gzip.open(metaData["path"],"rb") as f:
            file2 = f.read()
            f.close()
    
        xmlRootFile1 = ET.fromstring(file1)
        xmlRootFile2 = ET.fromstring(file2)

        a = []
        for xour in xmlRootFile1.iter("xournal"):
            a.append(xour)
        xournal = a[0]

    
        for page in xmlRootFile2.iter("page"):
           xournal.append(page)

        

        xmlstr = ET.tostring(xmlRootFile1,encoding="utf-8",method='xml')
        xml2 = ET.fromstring(xmlstr)
        gzXml = gzip.compress(xmlstr)

        print(gzXml)

        with open(self.metaData["path"],"wb") as f:
            f.write(gzXml)
            f.close()




    def run(self):
        if self.args == "move":
            try:
                self.moveBackgroundPdf()
            except ET.ParseError as e:
                print(self.metaData)
       elif self.args == "merge":
           for filE in self.Mergequeue:
               self.mergeWithFile(filE)_
