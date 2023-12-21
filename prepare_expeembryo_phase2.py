import os,glob
import sqlite3 
import argparse
from collections import defaultdict

import shutil

import numpy as np

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--phase_1_database_path",type=str,default="../database.db")
    parser.add_argument("--phase_2_database_path",type=str,default="../database_phase_2.db")
    
    args = parser.parse_args()

    shutil.copyfile(args.phase_1_database_path,args.phase_2_database_path)

    conn = sqlite3.connect(args.phase_2_database_path)
    c = conn.cursor()

    c.execute("select id from user where username != 'admin' and username != 'debug'")
    id_users = c.fetchall()

    already_seen_images = {}

    for id_user in id_users:

        c.execute(f"select id from video where idOwner=={id_user}")
        id_video = c.fetchone()

        c.execute(f"select nameImage from image where idVideo=={id_video}")
        image_names = c.fetchall()

        already_seen_images[id_user] = image_names

    c.execute("DELETE FROM image WHERE idVideo>0")
    


if __name__ == "__main__":
    main()