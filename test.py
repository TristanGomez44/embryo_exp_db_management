import argparse
import shutil 
import sqlite3
import os,sys
import numpy as np

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

    for img in imgs:
        
        img_name = img[5]

        query = f"select idVideo from image where nameImage=='{img_name}'"
        c.execute(query)
        idVideos = np.array(c.fetchall())[:,0]

        if len(set(idVideos.tolist())) != len(idVideos):
            print(img,"has duplicate idVideos",idVideos)

        if len(idVideos) != args.nb_of_annot_per_vid+1:
            print(img,"has",len(idVideos),"annotations.")
    
    csv = "idVideo,count\n"

    for idVideo in range(1,args.video_number+1):
        query = f"select COUNT(*) from image where idVideo=={idVideo}"
        c.execute(query)
        count = c.fetchone()

        csv += f"{idVideo},{count}\n"
    
    with open("img_nb_for_each_video.csv","w") as file:
        print(csv,file=file)

    conn.close()

if __name__ == "__main__":
    main()