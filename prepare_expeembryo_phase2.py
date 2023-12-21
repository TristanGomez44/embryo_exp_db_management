import os,glob
import sqlite3 
import argparse
from collections import defaultdict

import shutil

import numpy as np

from test import single_match_query
from prepare_expeembryon import DEBUG_VIDEO_NAME


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--phase_1_database_path",type=str,default="../database.db")
    parser.add_argument("--phase_2_database_path",type=str,default="../database_phase_2.db")
    parser.add_argument("--nb_of_annot_per_vid",type=int,default=7)    
    args = parser.parse_args()

    shutil.copyfile(args.phase_1_database_path,args.phase_2_database_path)

    conn = sqlite3.connect(args.phase_2_database_path)
    c = conn.cursor()

    c.execute("select id from user where username != 'admin' and username != 'debug'")
    id_users = c.fetchall()

    already_seen_during_phase_1 = defaultdict(lambda :[])

    id_videos = []

    for id_user in id_users:

        c.execute(f"select id from video where idOwner=={id_user[0]}")
        id_video = c.fetchone()[0]

        c.execute(f"select nameImage from image where idVideo=={id_video}")
        image_names = [image_name[0] for image_name in c.fetchall()]

        for image_name in image_names:
            already_seen_during_phase_1[image_name].append(id_video)

        id_videos.append(id_video)

    c.execute("DELETE FROM image WHERE idVideo>0")
    
    c.execute(f"select * from image where nameImage like 'F0%'")
    imgs = np.array(c.fetchall())

    debug_video_id = single_match_query(f"select id from video where name=='{DEBUG_VIDEO_NAME}'",c)[0]

    np.random.seed(0)

    videos = np.array([[id_videos[i],0] for i in range(len(id_videos))]).astype(float)

    for i,img in enumerate(imgs):

        if i %20==0:
            print(img,i,"/",len(imgs))

        videos_copy = np.copy(videos)

        already_seen = already_seen_during_phase_1[img[5]]
        for id_video in already_seen:
            videos_copy[videos_copy[:,0]==id_video,1] = np.inf

        np.random.shuffle(videos_copy)

        shuffled_videos = np.array(list(sorted(videos_copy,key=lambda x:x[1])))
        
        selected_vids = shuffled_videos[:args.nb_of_annot_per_vid]
        selected_video_inds = selected_vids[:,0]

        #print(len(set(already_seen).intersection(set(selected_video_inds))))
        #exit(0)

        for id_video in selected_video_inds:

            suffix = "_".join(img[5].split("_")[1:])

            #finding all focal planes corresponding to this image
            query = f"select nameImage from image where nameImage like '%{suffix}' and idVideo=={debug_video_id}"
            c.execute(query)
            focal_planes = c.fetchall()

            for plane in focal_planes:
                query = f"insert into image(score,idVideo,selected,timestamp,nameImage) values(0,{int(id_video)},False,0,'{plane[0]}')"
                c.execute(query)

            videos[np.argwhere(videos[:,0]==id_video)[0,0],1] += 1

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()