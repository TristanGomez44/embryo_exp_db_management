import argparse
import shutil 
import sqlite3
import os 
import numpy as np

from generate_logins import generate_logins

def make_backup(video_nb,database_path):
    database_copy_path = f"database_{video_nb}_videos.db"
    assert not os.path.exists(database_copy_path), "Database already exists"
    shutil.copyfile(database_path,database_copy_path)
    return database_copy_path

def clean_database(clean_script_path,c):
    with open(clean_script_path, 'r') as sql_file:
        sql_script = sql_file.read()
    c.executescript(sql_script)

def add_centers(center_list,c):
    center_set = list(set(center_list))
    center_id_dic = {}
    for i in range(len(center_set)):
        query = f"insert into center(id,name) values({i},'{center_set[i]}')"
        c.execute(query)
        center_id_dic[center_set[i]] = i
    return center_id_dic

def add_users_and_videos(login_list,sha256_passwd_list,center_id_list,c):

    video_names = []

    for i in range(len(login_list)):

        query = f"insert into user(username,password,isAdmin,isContributor,isExpert,idCenter) values ('{login_list[i]}','{sha256_passwd_list[i]}',0,0,1,{center_id_list[i]})"
        c.execute(query)

        query = f"select id from user where username=='{login_list[i]}'"
        c.execute(query)
        idUser = c.fetchone()[0]

        video_name = f'video{i}_{login_list[i]}'
        video_names.append(video_name)

        query = f"insert into video(patientName,idOwner,name,path,idCenter) values('',{idUser},'{video_name}','',{center_id_list[i]})"
        c.execute(query)

    return video_names

def add_images_to_videos(video_names,nb_of_annot_per_vid,c):

    c.execute(f"SELECT * FROM image WHERE nameImage LIKE 'F0%'")
    imgs = np.array(c.fetchall())

    np.random.seed(0)

    videos = np.array([[i,0] for i in range(len(video_names))])

    for img in imgs:

        np.random.shuffle(videos)

        selected_vids = np.array(list(sorted(videos,key=lambda x:x[1])))[:nb_of_annot_per_vid]

        print(img[0])
        print(selected_vids)

        selected_video_inds = selected_vids[:,0]

        for ind in selected_video_inds:

            query = f"select id from video where name=='{video_names[ind]}'"
            c.execute(query)
            idVideo = c.fetchone()[0]

            query = f"insert into image(score,idVideo,selected,timestamp,nameImage) values(0,{idVideo},False,0,'{img[5]}')"
            c.execute(query)

            videos[np.argwhere(videos[:,0]==ind)[0,0],1] += 1
        
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--database_path",type=str,default="../database.db")
    parser.add_argument("--cleaning_script_path",type=str,default="clean_database.sql")
    parser.add_argument("--seed",type=int,default=0)
    parser.add_argument("--nb_of_annot_per_vid",type=int,default=5)

    parser.add_argument("--user_nb_csv",type=str,default="comptes_expeembryon.csv")
    parser.add_argument("--logins_mdp_folder",type=str,default="logins")
    parser.add_argument("--password_size",type=int,default=10)
    args = parser.parse_args()

    login_list,sha256_passwd_list,center_list = generate_logins(args.logins_mdp_folder,args.user_nb_csv,args.password_size)

    video_nb = len(login_list)

    database_copy_path = make_backup(video_nb,args.database_path)

    conn = sqlite3.connect(database_copy_path)
    c = conn.cursor()
    
    clean_database(args.cleaning_script_path,c)
    center_id_dic = add_centers(center_list,c)
    center_id_list = [center_id_dic[center] for center in center_list]
    video_names = add_users_and_videos(login_list,sha256_passwd_list,center_id_list,c)
    add_images_to_videos(video_names,args.nb_of_annot_per_vid,c)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()