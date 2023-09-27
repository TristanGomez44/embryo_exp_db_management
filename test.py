import argparse
import shutil 
import sqlite3
import os,sys
import numpy as np

def single_match_query(query,c):
    c.execute(query)
    matching_rows = c.fetchall()
    assert len(matching_rows) == 1,f"Several rows match query='{query}':{matching_rows}"
    matching_row = matching_rows[0]
    return matching_row

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--video_number",type=int)
    parser.add_argument("--database_path",type=str)
    parser.add_argument("--nb_of_annot_per_vid",type=int,default=5)
    args = parser.parse_args()

    assert os.path.exists(args.database_path), "Database does not exists"

    conn = sqlite3.connect(args.database_path)
    c = conn.cursor()

    c.execute(f"SELECT * FROM image WHERE nameImage LIKE 'F0%'")
    imgs = np.array(c.fetchall())

    duplicate_ids = []
    wrong_annot_nb_ids = []

    for img in imgs:
        
        img_name = img[5]

        query = f"select idVideo from image where nameImage=='{img_name}'"
        c.execute(query)
        idVideos = np.array(c.fetchall())[:,0]

        if len(set(idVideos.tolist())) != len(idVideos):
            duplicate_ids.append((img,idVideos))

        if len(idVideos) != args.nb_of_annot_per_vid+1:
            wrong_annot_nb_ids.append((img,idVideos))
    
    assert len(duplicate_ids) == 0,f"Somes images are included several times in videos {duplicate_ids}"
    assert len(wrong_annot_nb_ids) == 0,f"Somes images have a wrong number of annotations {wrong_annot_nb_ids}"

    csv = "idVideo,count,video_name,idOwner,username\n"

    for idVideo in range(1,args.video_number+1):
        query = f"select COUNT(*) from image where idVideo=={idVideo}"
        c.execute(query)
        count = c.fetchone()[0]

        idOwner,video_name = single_match_query(f"select idOwner,name from video where id=={idVideo}",c)

        #query = f"select idOwner,name from video where id=={idVideo}"
        #c.execute(query)
        #matching_vids = c.fetchall()
        #assert len(matching_vids) == 1,f"Several videos have id={idVideo},{matching_vids}"
        #matching_vid = matching_vids[0]
        #idOwner,video_name = matching_vid
        
        username = single_match_query(f"select username from user where id=={idOwner}",c)[0]

        #query = f"select username from user where id=={idOwner}"
        #c.execute(query)
        #matching_users = c.fetchall()
        #assert len(matching_users) == 1,f"Several users have id={idOwner},{matching_users}"
        #matching_user = matching_users[0]
        #username = matching_user[0]

        csv += f"{idVideo},{count},{video_name},{idOwner},{username}\n"
    
    with open("img_nb_for_each_video.csv","w") as file:
        print(csv,file=file)

    conn.close()

if __name__ == "__main__":
    main()