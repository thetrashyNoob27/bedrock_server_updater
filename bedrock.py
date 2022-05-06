# coding: utf-8
import requests
import bs4
import re
def getVer(s):
    verPattern=re.compile(r'https?://.+/bedrock-server-(\d+.\d+.\d+.\d+).zip')
    res=verPattern.findall(s)
    for ver in res:
        return ver
    return ''

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

def getServerLink():
    headerStr=""":authority: www.minecraft.net
:method: GET
:path: /en-us/download/server/bedrock
:scheme: https
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
accept-encoding: gzip, deflate, br
accept-language: en-US,en;q=0.9
cache-control: max-age=0
dnt: 1
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36"""
    bedrockPage="https://www.minecraft.net/en-us/download/server/bedrock"
    headerStrList=headerStr.split("\n")
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
        
    getPageSuccess=True
    try:
        resp=requests.get(bedrockPage,headers=headers,timeout=10)
    except requests.ReadTimeout:
        print("request timeout")
        getPageSuccess=False

    if not getPageSuccess:
        return ''
    soup=bs4.BeautifulSoup(resp.text,'html.parser')
    serverLink=resolveLink(soup)
    return serverLink
        
