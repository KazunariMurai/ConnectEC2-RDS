# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 14:28:35 2018

@author: user
"""

# https://hack-le.com/mysqlclient-aws-rds/

from sshtunnel import SSHTunnelForwarder
#import mysql.connector
import MySQLdb
import boto3
from boto3 import Session

def AddCollection(collectionID, source):
    client = boto3.client('rekognition', 'us-east-2')
    response = client.index_faces(CollectionId=collectionId,
                                  Image={'S3Object':{'Bucket':'smart119-face-recognition','Name':source}},
                                  ExternalImageId='test',
                                  DetectionAttributes=['ALL',])
    response = json.dumps(response)
    
    return response

def AddCollectionFromLocalFile(collectionID, source):
    client = boto3.client('rekognition', 'us-east-2')
    key = open(source, 'rb')

    response = client.index_faces(CollectionId=collectionId,
                                  Image={	'Bytes' : key.read()	},
                                  ExternalImageId='test',
                                  DetectionAttributes=['ALL',])
    
    #print ('Faces in ' + source) 							
    for faceRecord in response['FaceRecords']:
        print ('done')
        print (faceRecord['Face']['FaceId'])
    
    return faceRecord['Face']['FaceId']

# SSH関連の設定
with SSHTunnelForwarder(
        ("52.14.168.73", 22), # 踏み台にするEC2のIP
        ssh_host_key=None,
        ssh_username="ec2-user",
        ssh_password=None,
        ssh_pkey="D:/SDK/ec2-key.pem",
        remote_bind_address=("smart119.cpar2vp3lmp9.us-east-2.rds.amazonaws.com", 3306), # RDSのエンドポイント
        local_bind_address=("127.0.0.1",1022) # 任意
#) as server:
) as tunnel:
    # RDSへの接続
    print("connecting RDS ...")
    conn = MySQLdb.connect(
            host="127.0.0.1",
            port=1022,
            user="master",
            db="test",
            passwd="mypassword",
            charset='utf8mb4')
    cur=conn.cursor()
    print("Connected!")
    
    # Process
    # Connect S3
    #cur.execute("CREATE TABLE test.face(aws_id varchar(50), name varchar(50))")
    cur.execute("select * from face;")

    region="us-east-2"
    maxResults=2
    tokens=True

    client=boto3.client('rekognition', region)
    collectionId='smart119-test'
        
    response=client.list_faces(CollectionId=collectionId,
                               MaxResults=maxResults)

    # テーブルが存在しなければ作成
    try:
        # id, nameだけのテーブル，idが主キー
        cur.execute("""CREATE TABLE IF NOT EXISTS `sample` (
            `id` int(11) NOT NULL,
            `name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
            PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
    except MySQLdb.Error as e:
        print('MySQLdb.Error: ', e)

    
    # 顔画像追加 人物名を手動入力する必要あり
    """
    # Search all faceID in the collection
    print('Faces in collection ' + collectionId)       

    while tokens:

        faces=response['Faces']
        
        for face in faces:
            print (face['FaceId'])
            try:
                print("Add face to DB")
                name = input()
                cur.execute("insert into sample values(%s, %s)", [face['FaceId'], name]) # 名前は手動入力
                conn.commit()
            except:
                conn.rollback()
                raise

        if 'NextToken' in response:
            nextToken=response['NextToken']
            response=client.list_faces(CollectionId=collectionId, NextToken=nextToken,MaxResults=maxResults)
        else:
            tokens=False    
    """
    
    # コレクションから顔画像検索
    s3res = Session().resource('s3')
    bucket = s3res.Bucket('smart119-face-recognition')
    keys = [obj.key for obj in bucket.objects.all()]
    collectionId='smart119-test'
    threshold = 70
    maxFaces=10
    #fileName='Aaron_Eckhart/Aaron_Eckhart_0002.jpg'
    source = "D:/data/Face data/lfw-a/lfw/Aaron_Eckhart/Aaron_Eckhart_0005.jpg" # local file
    
    faceID = AddCollectionFromLocalFile(collectionId, source)
    
    response=client.search_faces(CollectionId=collectionId,
                                FaceId=faceID,
                                FaceMatchThreshold=threshold,
                                MaxFaces=maxFaces)
    
    
    faceMatches=response['FaceMatches']
    print ('Matching faces')
    for match in faceMatches:
        print ('FaceId:' + match['Face']['FaceId'])
        print ('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
        print ()        
    
        matchedFaceId=match['Face']['FaceId']
    
        # SQLテーブルから一致する顔画像を検索
        cur.execute('select name from sample where id=' + matchedFaceId + ';')
    
    conn.close()
