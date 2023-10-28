import sys
import argparse
import sqlite3
from datetime import datetime
import shutil
import secrets
import string
import random

import numpy as np

from generate_logins_and_mails import hash_passwd,generate_passwd,write_email,make_logins_csv
from prepare_expeembryon import add_users_and_videos,DEBUG_VIDEO_NAME
from test import single_match_query

def generate_logins_and_passwd(user_nb,alphabet,password_size,login_pref):
    login_list = []
    passwd_list = []
    hashed_passwd_list = []

    for i in range(user_nb):
        login = login_pref+str(i)  
        passwd = generate_passwd(alphabet,password_size)
        hashed_passwd = hash_passwd(passwd)

        login_list.append(login)
        passwd_list.append(passwd)
        hashed_passwd_list.append(hashed_passwd)

    return login_list,passwd_list,hashed_passwd_list

def add_imgs_to_videos(imgs_and_annot_nb,user_nb,video_names,img_per_participant,debug_video_id,c):
    for i in range(user_nb):
        imgs_and_annot_nb = list(sorted(imgs_and_annot_nb,key=lambda x:x[1]))

        idVideo = single_match_query(f"select id from video where name=='{video_names[i]}'",c)[0]

        imgs_to_add = []
        for j in range(img_per_participant):
            img = imgs_and_annot_nb[j][0]
            imgs_to_add.append(img)
            imgs_and_annot_nb[j][1] += 1
            
            suffix = "_".join(img[0].split("_")[1:])

            #finding all focal planes corresponding to this image
            query = f"select nameImage from image where nameImage like '%{suffix}' and idVideo=={debug_video_id}"
            c.execute(query)
            focal_planes = c.fetchall()

            for plane in focal_planes:
                query = f"insert into image(score,idVideo,selected,timestamp,nameImage) values(0,{idVideo},False,0,'{plane[0]}')"
                c.execute(query)

def make_img_and_annot_nb_array(debug_video_id,c,nb_of_annot_per_vid):

    c.execute(f"select nameImage from image where nameImage like 'F0%' and idVideo=={debug_video_id}")
    imgs = np.array(c.fetchall())

    annot_nb = []

    for img in imgs:
        nameImage = img[0]
        query = f"select idVideo from image where nameImage=='{nameImage}'"
        c.execute(query)
        idVideos = c.fetchall()

        assert len(idVideos) ==  len(set(idVideos)),f"Image {nameImage} was inserted several times in the image table with the same video"

        assert len(idVideos) >= nb_of_annot_per_vid+1,f"Image {nameImage} has an incorrect number of videos assigned:{len(idVideos)}"

        annot_nb.append(len(idVideos))
        
    imgs_and_annot_nb_tuple = list(zip(imgs,annot_nb))
    imgs_and_annot_nb_list = []
    for img,annot_nb in imgs_and_annot_nb_tuple:
        imgs_and_annot_nb_list.append([img,annot_nb])

    #imgs_and_annot_nb = np.array(imgs_and_annot_nb)
    random.shuffle(imgs_and_annot_nb_list)
    
    return imgs_and_annot_nb_list

def check_if_prefix_exists(prefix,c):
    c.execute(f"select username from user where username like '{prefix}%'")
    assert len(c.fetchall()) == 0,"Prefix already exists in database"

def make_backup(database_path,debug,debug_database_path="database_debug.db"):
    date_time = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    database_copy_path = f"database_{date_time}.db"
    shutil.copyfile(database_path,database_copy_path)
    
    if debug:
        shutil.copyfile(database_path,debug_database_path)
        database_path = debug_database_path

    return database_path

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--database_path",type=str,default="./database.db")
    parser.add_argument("--coordinator_email",type=str)  
    parser.add_argument("--user_nb",type=int)
    parser.add_argument("--login_prefix",type=str)
    parser.add_argument("--img_per_participant",type=int,default=135)

    parser.add_argument("--debug",action="store_true")

    parser.add_argument("--mail_folder",type=str,default="./mails")
    parser.add_argument("--login_folder",type=str,default="./logins")
    parser.add_argument("--password_size",type=int,default=10)
    parser.add_argument("--mail_template_path",type=str,default="mail_template.txt")
    parser.add_argument("--email_name_path",type=str,default="email_names.csv")
    parser.add_argument("--nb_of_annot_per_vid",type=int,default=5)

    args = parser.parse_args()

    database_path = make_backup(args.database_path,args.debug)
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    alphabet = string.ascii_letters + string.digits
    check_if_prefix_exists(args.login_prefix,c)

    c.execute("select id from center")
    centerId = np.array(c.fetchall()).astype(int).max() + 1
    c.execute(f"insert into center(id,name) values({centerId},'{args.login_prefix}')")

    login_list,passwd_list,hashed_passwd_list = generate_logins_and_passwd(args.user_nb,alphabet,args.password_size,args.login_prefix)

    logins_csv = make_logins_csv(login_list,passwd_list,args.login_folder,args.login_prefix)

    write_email(logins_csv,args.mail_folder,args.coordinator_email,args.mail_template_path,args.email_name_path,args.user_nb)

    video_names = add_users_and_videos(login_list,hashed_passwd_list,[centerId for _ in range(args.user_nb)],c)

    debug_video_id = single_match_query(f"select id from video where name=='{DEBUG_VIDEO_NAME}'",c)[0]

    imgs_and_annot_nb = make_img_and_annot_nb_array(debug_video_id,c,args.nb_of_annot_per_vid)
    
    add_imgs_to_videos(imgs_and_annot_nb,args.user_nb,video_names,args.img_per_participant,debug_video_id,c)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()