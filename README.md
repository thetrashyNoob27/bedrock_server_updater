# bedrock_server_updater
update linux bedrock server 

process is:

0.check args, is server and backup and download location RW-able?

  if not then quit
  
1.download server release page using cURL.(https://www.minecraft.net/en-us/download/server/bedrock)

2.get the LINUX server file link(https://minecraft.azureedge.net/bin-linux/bedrock-server-1.18.32.02.zip)

3.read version number by server file link(1.18.32.02)

4.if not download,then download server file(DOWNLOAD_PATH/bedrock-server-1.18.32.02.zip)

5.compair version by read YOUR_SERVER_DIR/server_version.txt(this script create this file)

  if not equal now version OR --fu is set
  
  then continue.
  
  else quit.
  
6.execute pre-upgrade command

  if fail then quit.
  
7.backup using tar -I 'gzip -6' to BACKUP_PATH/

  if fail then quit.
  
8.extract server zip to YOUR_SERVER_DIR/,but dont overwrite ['server.properties','permissions.json','allowlist.json'] if present.and create server_version.txt

9.excute post-upgrade command


  
  
for example
  
./bedrock-update.py -s /srv/bedrock -b /opt/bedrock-update/backup/ -d /opt/bedrock-update/download/ --pre "systemctl stop bedrock" --post "systemctl start bedrock"

i dont know why with the same haders python request can not get server release page,but cURL can. if sone one know please tell me.im really confused.
