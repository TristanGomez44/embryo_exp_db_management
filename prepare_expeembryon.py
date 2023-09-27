import argparse
import shutil 
import sqlite3
import os 
import numpy as np

from generate_logins_and_mails import generate_logins_and_mails,hash_passwd
from test import single_match_query

def make_backup(video_nb,database_path):
    database_copy_path = f"database_{video_nb}_videos.db"
    assert not os.path.exists(database_copy_path), "Database already exists"
    shutil.copyfile(database_path,database_copy_path)
    return database_copy_path

def add_admin_and_debug_user(debug_user_name,c):
    admin_psswd = input("Admin password:")
    debug_psswd = input("Debug password:")

    hashed_admin_passwd = hash_passwd(admin_psswd)
    hashed_debug_passwd = hash_passwd(debug_psswd)

    c.execute(f"insert into user (username,password,isAdmin,isContributor,isExpert,idCenter) values('admin','{hashed_admin_passwd}',1,0,0,0)")
    c.execute(f"insert into user (username,password,isAdmin,isContributor,isExpert,idCenter) values('{debug_user_name}','{hashed_debug_passwd}',0,1,1,0)")

def add_debug_video(debug_user_name,c,debug_video_name="allimages"):
    debug_user_id = single_match_query(f"select id from user where username=='{debug_user_name}'",c)[0]
    
    c.execute(f"insert into video (id,patientName,idOwner,name,path,idCenter) values(0,'',{debug_user_id},'{debug_video_name}','../uploads/dataset',1)")

    debug_video_id = single_match_query(f"select id from video where name=='{debug_video_name}'",c)[0]

    c.execute(f"update image set idVideo == {debug_video_id}")

def clean_database(clean_script_path,c):
    with open(clean_script_path, 'r') as sql_file:
        sql_script = sql_file.read()
    c.executescript(sql_script)

def add_centers(center_list,c):
    center_set = list(set(center_list))
    center_id_dic = {}
    for i in range(len(center_set)):
        c.execute(f"insert into center(id,name) values({i},'{center_set[i]}')")
        center_id_dic[center_set[i]] = i
    return center_id_dic

def add_users_and_videos(login_list,hashed_passwd_list,center_id_list,c):

    video_names = []

    for i in range(len(login_list)):

        query = f"insert into user(username,password,isAdmin,isContributor,isExpert,idCenter) values ('{login_list[i]}','{hashed_passwd_list[i]}',0,0,1,{center_id_list[i]})"
        c.execute(query)

        c.execute(f"select id from user where username=='{login_list[i]}'")
        idUser = c.fetchone()[0]

        video_name = f'video{i}_{login_list[i]}'
        video_names.append(video_name)

        query = f"insert into video(patientName,idOwner,name,path,idCenter) values('',{idUser},'{video_name}','',{center_id_list[i]})"
        c.execute(query)

    return video_names

def add_images_to_videos(video_names,nb_of_annot_per_vid,c):

    c.execute(f"select * from image where nameImage like 'F0%'")
    imgs = np.array(c.fetchall())

    np.random.seed(0)

    videos = np.array([[i,0] for i in range(len(video_names))])

    for img in imgs:

        np.random.shuffle(videos)

        selected_vids = np.array(list(sorted(videos,key=lambda x:x[1])))[:nb_of_annot_per_vid]
        selected_video_inds = selected_vids[:,0]

        for ind in selected_video_inds:

            c.execute(f"select id from video where name=='{video_names[ind]}'")
            idVideo = c.fetchone()[0]

            query = f"insert into image(score,idVideo,selected,timestamp,nameImage) values(0,{idVideo},False,0,'{img[5]}')"
            c.execute(query)

            videos[np.argwhere(videos[:,0]==ind)[0,0],1] += 1
        
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--database_path",type=str,default="../database_25-07-2023.db")
    parser.add_argument("--cleaning_script_path",type=str,default="clean_database.sql")
    parser.add_argument("--seed",type=int,default=0)
    parser.add_argument("--nb_of_annot_per_vid",type=int,default=5)
    parser.add_argument("--participant_target_nb",type=int,default=70)
    
    parser.add_argument("--debug_user_name",type=str,default="debug")

    parser.add_argument("--user_nb_csv",type=str,default="comptes_expeembryon.csv")
    parser.add_argument("--logins_and_mail_folder",type=str,default=".")
    parser.add_argument("--password_size",type=int,default=10)
    parser.add_argument("--mail_template_path",type=str,default="mail_template.txt")
    parser.add_argument("--email_name_path",type=str,default="email_names.csv")
    args = parser.parse_args()

    login_list,hashed_passwd_list,center_list = generate_logins_and_mails(args.logins_and_mail_folder,args.user_nb_csv,args.password_size,args.mail_template_path,args.email_name_path,args.participant_target_nb)

    video_nb = len(login_list)

    database_copy_path = make_backup(video_nb,args.database_path)

    conn = sqlite3.connect(database_copy_path)
    c = conn.cursor()
    
    clean_database(args.cleaning_script_path,c)
    add_admin_and_debug_user(args.debug_user_name,c)
    add_debug_video(args.debug_user_name,c)
    center_id_dic = add_centers(center_list,c)
    center_id_list = [center_id_dic[center] for center in center_list]
    video_names = add_users_and_videos(login_list,hashed_passwd_list,center_id_list,c)
    add_images_to_videos(video_names,args.nb_of_annot_per_vid,c)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()