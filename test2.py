import argparse
import shutil 
import sqlite3
import os,sys
import numpy as np

def single_match_query(query,c):
    c.execute(query)
    matching_rows = c.fetchall()
    assert len(matching_rows) == 1,f"Several or zero rows match query='{query}':{matching_rows}"
    matching_row = matching_rows[0]
    return matching_row

def get_video_ids(c1):
    c1.execute("select id from user where username != 'admin' and username != 'debug'")
    id_users = c1.fetchall()
    id_videos = []
    for id_user in id_users:
        c1.execute(f"select id from video where idOwner=={id_user[0]}")
        id_video = c1.fetchone()[0]
        id_videos.append(id_video)
    return id_videos 

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--phase_1_database_path",type=str)
    parser.add_argument("--phase_2_database_path",type=str)    
    parser.add_argument("--nb_of_annot_per_vid",type=int,default=5)
    parser.add_argument("--debug_user_name",type=str,default="debug")

    args = parser.parse_args()

    conn1 = sqlite3.connect(args.phase_1_database_path)
    c1 = conn1.cursor()

    conn2 = sqlite3.connect(args.phase_2_database_path)
    c2 = conn2.cursor()

    id_videos = get_video_ids(c1)

    for id_video in id_videos:

        c1.execute(f"select nameImage from image where idVideo=={id_video}")
        image_names_c1 = c1.fetchall()

        c2.execute(f"select nameImage from image where idVideo=={id_video}")
        image_names_c2 = c2.fetchall()  

        assert len(set(image_names_c1).intersection(set(image_names_c2))) == 0

    conn1.close()
    conn2.close()

if __name__ == "__main__":
    main()