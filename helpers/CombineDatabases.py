#import requests
import sys
#import hashlib
#import os
from os import scandir, remove, rmdir
from os.path import exists, isfile, join, isdir, basename
import mysql.connector
from pathlib import Path
import sqlite3
from time import sleep
from tqdm import tqdm
from tqdm.auto import trange


def CopyMedia(oldCursor, newDb, dbDesc, userId):
    # with sqlite3.connect('C:\\Temp\\data.db') as con, mysql.connector.connect(host="192.168.1.162", user="root", password="Jnmjvt19!", database="vue_data", port=6603) as nConn:
    newCursor = newDb.cursor()
    oldCursor.execute("SELECT COUNT(*) as rowcount FROM medias")
    oRes = oldCursor.fetchone()
    mediaRows = oRes[0]
    oldCursor.execute(
        "SELECT COUNT(*)FROM (SELECT DISTINCT post_id,text FROM (SELECT post_id,text FROM posts UNION SELECT post_id,text FROM messages) x WHERE length(text)>0) x")
    oRes = oldCursor.fetchone()
    postRows = oRes[0]
    cnt = 1
    totalCnt = 1
    with tqdm(total=mediaRows+postRows, desc=dbDesc, position=1, leave=False) as pbar:
        # for srow in cur.execute("SELECT DISTINCT post_id,text FROM (SELECT post_id,text FROM posts UNION SELECT post_id,text FROM messages) x WHERE length(text)>0 ORDER BY post_id LIMIT 171976"):
        #     sql = "INSERT INTO Posts (post_id,post_text) VALUES (%s,%s)"

        #     # print(sql)
        #     newCur.execute(sql, (srow[0], srow[1]))
        for srow in oldCursor.execute("SELECT m.media_id,m.post_id,m.link,m.filename,m.size,m.api_type,m.media_type,m.preview,m.downloaded,m.created_at,m.duration,m.thumbnail FROM medias m"):
            sql = "INSERT IGNORE INTO medias (user_id,media_id,post_id,link,filename,size,api_type,media_type,preview,downloaded,created_at,duration,thumbnail) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

            # print(sql)
            newCursor.execute(sql, (userId, srow[0], srow[1], srow[2], srow[3], srow[4],
                              srow[5], srow[6], srow[7], srow[8], srow[9], srow[10], srow[11]))

            totalCnt += 1
            if(cnt == 4 or totalCnt > mediaRows-5):
                newDb.commit()
                cnt = 0
            cnt += 1
            pbar.update(1)

        cnt = 1
        totalCnt = 1
        for srow in oldCursor.execute("SELECT DISTINCT post_id,text FROM (SELECT post_id,text FROM posts UNION SELECT post_id,text FROM messages) x WHERE length(text)>0 ORDER BY post_id"):
            sql = "INSERT IGNORE INTO Posts (post_id,post_text) VALUES (%s,%s)"

            # print(sql)
            newCursor.execute(sql, (srow[0], srow[1]))

            totalCnt += 1
            if(cnt == 4 or totalCnt > postRows-5):
                newDb.commit()
                cnt = 0
            cnt += 1
            pbar.update(1)

    newCursor.close()
# newdb.close()


def CopyData(dbPath):
    parts = dbPath.split('\\')
    username = parts[len(parts)-2]

    with sqlite3.connect(dbPath) as con, mysql.connector.connect(host="192.168.1.162", user="root", password="Jnmjvt19!", database="vue_data", port=6603) as nConn:
        try:
            cur = con.cursor()
            nCur = nConn.cursor()
            # sql = "ATTACH DATABASE '{}' AS usr;".format(dbPath)
            # cur.execute(sql)

            userId = 0

            nCur.execute(
                "SELECT userId FROM Users WHERE username='{}'".format(username))
            res = nCur.fetchone()
            if(res is not None):
                userId = res[0]

            if(userId == 0):
                cur.execute("SELECT user_id FROM messages LIMIT 1")
                res = cur.fetchone()
                if(res is None):
                    print("Unable to Lookup UserId for "+username)
                    return
                else:
                    userId = res[0]

                    nCur.execute("INSERT OR REPLACE INTO Users (userId,username) VALUES (?,?)",
                                 (userId, username))
                    nCur.commit()

            cur.execute(
                "SELECT sql FROM main.sqlite_master WHERE tbl_name='medias' and type='table'")
            res = cur.fetchone()

            # sql = "INSERT INTO medias (media_id,user_id,post_id,link,filename,size,api_type,media_type,preview,downloaded,created_at,thumbnail,duration) SELECT m1.media_id,{},m1.post_id,m1.link,m1.filename,m1.size,m1.api_type,m1.media_type,m1.preview,m1.downloaded,m1.created_at,m1.thumbnail,m1.duration FROM usr.medias m1 LEFT JOIN medias m2 ON m1.media_id=m2.media_id WHERE m2.id IS NULL".format(userId)

            if("thumbnail" not in res[0]):
                cur.execute("ALTER TABLE medias ADD COLUMN thumbnail text")
                con.commit()
            if("duration" not in res[0]):
                cur.execute("ALTER TABLE medias ADD COLUMN duration INTEGER")
                con.commit()

            CopyMedia(cur, nConn, username, userId)
            #res = cur.execute(sql)
            # con.commit()

            #cur.execute("INSERT INTO posts (post_id,text,created_at,user_id) SELECT t1.post_id,t1.text,t1.created_at,{} FROM usr.posts t1 LEFT JOIN posts t2 ON t1.post_id=t2.post_id WHERE t2.id IS NULL".format(userId))
            # con.commit()

            #cur.execute("INSERT INTO messages (post_id,text,created_at,user_id) SELECT t1.post_id,t1.text,t1.created_at,{} FROM usr.messages t1 LEFT JOIN messages t2 ON t1.post_id=t2.post_id WHERE t2.id IS NULL".format(userId))
            # con.commit()
            cur.close()
            nCur.close()
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)
            print("Error with "+username)


dbFiles = []


def process_root(dir):
    for d in [f for f in scandir(dir) if f.is_dir()]:
        dbPath = join(d, 'user_data.db')
        if(exists(dbPath)):
            dbFiles.append(dbPath)


def CombineFiles():
    with tqdm(total=len(dbFiles), unit='files', desc='Database Files', position=0) as mbar:
        for d in [d for d in dbFiles if d is not None]:
            parts = d.split('\\')
            username = parts[len(parts)-2]
            mbar.set_postfix(file=username, refresh=False)
            CopyData(d)
            mbar.update(1)
