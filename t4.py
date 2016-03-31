import ftplib

server = 'ssmsynology.synology.me'
username = 'nickisverygood'
password = 'sbi8844848'
ftp_connection = ftplib.FTP(server, username, password)
remote_path = "/homes/nickisverygood/DynamicMindMap/"
ftp_connection.cwd(remote_path)
fh = open("NetworkDump.json", 'rb')
ftp_connection.storbinary('STOR NetworkDump.json', fh)
ftp_connection.retrbinary('RETR %s' % "NetworkDump.json", fh.write)

fh.close()