# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 14:28:35 2018

@author: user
"""

from sshtunnel import SSHTunnelForwarder
#import mysql.connector
import MySQLdb

# SSH関連の設定
with SSHTunnelForwarder(
        ("3.16.164.120", 22),
        ssh_host_key=None,
        ssh_username="ec2-user",
        ssh_password=None,
        ssh_pkey="D:/SDK/ec2-key.pem",
        remote_bind_address=("smart119.cpar2vp3lmp9.us-east-2.rds.amazonaws.com", 3306),
        local_bind_address=("127.0.0.1",10022)
#) as server:
) as tunnel:
    # RDSへの接続
    print("connecting RDS ...")
    conn = MySQLdb.connect(
            host="127.0.0.1",
            port=10022,
            user="master",
            db="test",
            passwd="mypassword",
            charset='utf8mb4')
    c=conn.cursor()
    print("Connected!")
    
    #
    # DBへの処理
    #
    
    conn.close()
