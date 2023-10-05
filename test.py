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
    parser.add_argument("--debug_user_name",type=str,default="debug")
    args = parser.parse_args()

    assert os.path.exists(args.database_path), "Database does not exists"

    conn = sqlite3.connect(args.database_path)
    c = conn.cursor()

    debug_user_id = single_match_query(f"select id from user where username=='{args.debug_user_name}'",c)[0]
    debug_vid_id = single_match_query(f"select id from video where idOwner=={debug_user_id}",c)[0]
    
    c.execute(f"SELECT * FROM image WHERE nameImage LIKE 'F0%' and idVideo=={debug_vid_id}")
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
    assert len(wrong_annot_nb_ids) == 0,f"Somes images have a incorrect number of videos {wrong_annot_nb_ids}"

    csv = "idVideo,count,video_name,idOwner,username\n"

    for idVideo in range(1,args.video_number+1):

        query = f"select COUNT(*) from image where idVideo=={idVideo} and nameImage like 'F0%'"
        c.execute(query)
        count = c.fetchone()[0]

        idOwner,video_name = single_match_query(f"select idOwner,name from video where id=={idVideo}",c)
        username = single_match_query(f"select username from user where id=={idOwner}",c)[0]

        csv += f"{idVideo},{count},{video_name},{idOwner},{username}\n"
    
    with open("img_nb_for_each_video.csv","w") as file:
        print(csv,file=file)

    conn.close()

if __name__ == "__main__":
    main()