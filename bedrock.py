#!/usr/bin/env python3
# coding: utf-8
from operator import truediv
import requests
import bs4
import re
import os
import datetime
import io
import zipfile

def workingHeaders():
    headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
 'accept-encoding': 'gzip, deflate, br',
 'accept-language': 'en-US,en;q=0.9',
 'cache-control': 'max-age=0',
 'dnt': '1',
 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
 'sec-ch-ua-mobile': '?0',
 'sec-ch-ua-platform': '"Windows"',
 'sec-fetch-dest': 'document',
 'sec-fetch-mode': 'navigate',
 'sec-fetch-site': 'none',
 'sec-fetch-user': '?1',
 'upgrade-insecure-requests': '1',
 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'}
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

def updateServer(serverZip,serverDir):
    excludeFiles=['server.properties','permissions.json','allowlist.json']
    zipObj=zipfile.ZipFile(io.BytesIO(serverZip),'r')
    for f in zipObj.namelist():
        if f in excludeFiles:
            continue
        zipObj.extract(f,serverDir)

    return

if __name__ == "__main__":
    #settings:
    serverDir='/srv/bedrock'
    backupDir=os.path.join(getThisScriptPath(),'backup')
    afterUpdateCMD='systemctl restart bedrock'
    outPutDir=getThisScriptPath()

    link=getServerLink()
    if link =='':
        exit(1)
        print("get server zip file fail")
    ver=getVer(link)
    print("%s" %(link))

    print("current server version:%s" %(ver))
    allreadyDownloaded=isVerPresent(ver,outPutDir)
    print("server allready downlaoded:%s" %(str(allreadyDownloaded)))
    if allreadyDownloaded:
        exit(0)
    [downloadSuccess,serverzip]=downloadServerFile(link,outPutDir,headers=workingHeaders())
    print("download success:%s" %(str(downloadSuccess)))
    if not downloadSuccess:
        exit(1)
    print("backup old server.")
    backupSuccess=backupServer(serverDir,backupDir)
    if not backupSuccess:
        print('backup fail.abort update.')
        exit(2)

    zipf=open('/tmp/bedrock-server-1.18.32.02.zip','rb')
    serverzip=zipf.read()
    zipf.close()
    updateServer(serverzip,serverDir)

