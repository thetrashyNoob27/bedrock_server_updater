#!/usr/bin/env python3
# coding: utf-8
from nturl2path import pathname2url
from operator import truediv
import requests
import bs4
import re
import os
import datetime
import io
import zipfile
import argparse

def workingHeaders():
    headers={
    'authority': 'www.minecraft.net',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'dnt': '1',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
}
    return headers

def getVer(s):
    verPattern=re.compile(r'\.*bedrock-server-(\d+.\d+.\d+.\d+).zip')
    res=verPattern.findall(s)
    for ver in res:
        return ver
    return ''

def isVerPresent(verStr,dir):
    fileList=[ f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir,f))]
    verList=[]
    for f in fileList:
        ver=getVer(f)
        if ver !='':
            verList.append(ver)
    
    if verStr in verList:
        return True
    else:
        return False

def getServerName(s):
    filePattern=re.compile(r'https?://.+/(bedrock-server-\d+.\d+.\d+.\d+.zip)')
    fileName=filePattern.findall(s)
    for name in fileName:
        return name
    return ''

def resolveLink(soup):
    a_list=soup.find_all('a',{"data-platform":"serverBedrockLinux"})
    serverFileNamePattern=re.compile(r'https?://.+/bedrock-server-(\d+.\d+.\d+.\d+).zip')

    for a in a_list:
        maybeLink=a.get("href")
        if serverFileNamePattern.fullmatch(maybeLink):
            return maybeLink
        else:
            continue
    return ''

def downloadServerFile(link,dir,headers={}):
    downloadSuccess=False
    try:
        resp=requests.get(link,headers,timeout=600)
        downloadSuccess=True
    except requests.ReadTimeout:
        print("server download  timeout %s" %(link))
    if not downloadSuccess:
        return downloadSuccess,bytes()
    name=getServerName(link)
    filePath=os.path.join(dir,getServerName(link))
    zipFile=open(filePath,'wb')
    content=resp.content
    zipFile.write(content)
    zipFile.close()
    return downloadSuccess,content
        

def getThisScriptPath():
    try:
        path=os.path.dirname(os.path.realpath(__file__))
    except NameError:
        return ''
    return path

def headerStr2Dict(str):
    headerStrList=str.split("\n")
    headers={}
    for h in headerStrList:
        hsplit=h.split(":")
        if h[0]==':':
            k=":"
            k+=hsplit[1]
            v=hsplit[2]
            continue
        else:
            k=hsplit[0]
            v=hsplit[1]
        headers[k]=v.lstrip()
    return headers

def getServerLink():
    bedrockPage="https://www.minecraft.net/en-us/download/server/bedrock"
    curlCmd="""curl 'https://www.minecraft.net/en-us/download/server/bedrock' \
  -H 'authority: www.minecraft.net' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'dnt: 1' \
  -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: none' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36' \
  --compressed"""
    r=os.popen(curlCmd).read()
    soup=bs4.BeautifulSoup(r,'html.parser')
    serverLink=resolveLink(soup)
    return serverLink

    getPageSuccess=True
    try:
        resp=requests.get(bedrockPage,headers=workingHeaders(),timeout=600)
    except requests.ReadTimeout:
        print("release page request timeout")
        getPageSuccess=False

    if not getPageSuccess:
        return ''
    soup=bs4.BeautifulSoup(resp.text,'html.parser')
    serverLink=resolveLink(soup)
    return serverLink

def removeTralingPathSeparator(p):
    if p.endswith(os.sep):
        return p[:-1]
    else:
        return p
        
def backupServer(serverDir,outputDir):
    serverDir=removeTralingPathSeparator(serverDir)
    outputDir=removeTralingPathSeparator(outputDir)
    datetimeStr=datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    tarName="bedrock-backup-%s.tar.gz" %(datetimeStr)
    outputFIle=os.path.join(outputDir,tarName)
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    cmd="tar -I 'gzip -6' -C %s -cf %s %s/" %(os.path.dirname(serverDir),outputFIle,os.path.basename(serverDir))
    print(cmd)
    retVar=os.system(cmd)
    if retVar==0:
        return True
    return False

def updateServer(serverZip,version,serverDir):
    dontOverWrite=['server.properties','permissions.json','allowlist.json']
    excludeFiles=[]
    for f in dontOverWrite:
        if os.path.exists(os.path.join(serverDir,f)):
            excludeFiles.append(f)
    zipObj=zipfile.ZipFile(io.BytesIO(serverZip),'r')
    for f in zipObj.namelist():
        if f in excludeFiles:
            continue
        zipObj.extract(f,serverDir)

    version_file=open(os.path.join(serverDir,"server_version.txt"),'w')
    version_file.write(version)
    version_file.close()
    return

def serverDirVersion(serverDir):
    try:
        version_file=open(os.path.join(serverDir,"server_version.txt"),'r')
        versionStr=version_file.read()
        version_file.close()
    except FileNotFoundError:
        return "0.0.0.0"
    return versionStr

def argParser():
    p=argparse.ArgumentParser(description='minecraft bedrock server update')
    p.add_argument('-s',nargs='?',help='bedrock server location')
    p.add_argument('-b',nargs='?',help='server backup output location(default script location)')
    p.add_argument('-d',nargs='?',help='server file download dir(default script location)')
    p.add_argument('--pre',help='server pre-upgrade command')
    p.add_argument('--post',help='server post-upgrade command')
    updateOption = p.add_mutually_exclusive_group()
    updateOption.add_argument('--jd', action='store_true',help='just download.')
    updateOption.add_argument('--dnu', action='store_true',help='download and update.(default)')
    updateOption.add_argument('--fu',action='store_true',help='force update')
    settings=p.parse_args()
    print(settings)
    return settings

def testDirAccessable(path,pathName):
    #print("%s:%s" %(pathName,path))
    if os.path.exists(path):
        if os.access(path,os.R_OK|os.W_OK):
            return True
        else:
            print("%s:dir cant r/w" %(pathName))
    else:
        print("%s:path is not exist." %(pathName))
    return False

if __name__ == "__main__":
    #settings:
    settings=argParser()
    
    serverDir=settings.s
    if serverDir is None:
        print("must set server dir.")
        exit(1)
    if not (settings.b is None):
        backupDir=settings.b
    else:
        backupDir=getThisScriptPath()
    
    if not settings.d is None:
        downloadDir=settings.d
    else:
        downloadDir=getThisScriptPath()

    #working mode
    if settings.jd|settings.dnu|settings.fu==False:
        settings.dnu=True

    #test location R/W
    dirOK=True
    if not settings.jd:
        dirOK&=testDirAccessable(serverDir,"server dir")
    if not settings.jd:
        dirOK&=testDirAccessable(backupDir,"backup dir")
    dirOK&=testDirAccessable(downloadDir,"server download dir")
    if not dirOK:
        exit(1)
    
    #get newest version 
    link=getServerLink()
    if link =='':
        print("get server version fail.")
        exit(1)
    ver=getVer(link)
    print("%s" %(link))
    print("current server version:%s" %(ver))

    #download server zip file
    allreadyDownloaded=isVerPresent(ver,downloadDir)
    print("server allready downlaoded:%s" %(str(allreadyDownloaded)))
    if not allreadyDownloaded:
        print("start server download.")
        [downloadSuccess,serverzip]=downloadServerFile(link,downloadDir,headers=workingHeaders())
        print("download success:%s" %(str(downloadSuccess)))
        if not downloadSuccess:
            exit(1)
    elif not settings.jd:
        serverFileName=getServerName(link)
        serverFile=open(os.path.join(downloadDir,serverFileName),'rb')
        serverzip=serverFile.read()
        serverFile.close()

    if settings.jd==True:
        #just download server
        exit(0)

    serverIsLatested=serverDirVersion(serverDir)==ver

    if serverIsLatested and not settings.fu:
        print("server is newest.")
        exit(0)

    

    print("backup old server.")
    if not settings.pre is None:
        res=os.system(settings.pre)
        if res!=0:
            print("pre-update command fail.")
    backupSuccess=backupServer(serverDir,backupDir)
    if not backupSuccess:
        print('backup fail.abort update.')
        if not settings.post is None:
            res=os.system(settings.post)
            if res!=0:
                print("post-update command fail.")
        exit(2)
    print("backup server success.")

    print("update server...")
    updateServer(serverzip,ver,serverDir)
    if not settings.post is None:
        res=os.system(settings.post)
        if res!=0:
            print("post-update command fail.")
    

