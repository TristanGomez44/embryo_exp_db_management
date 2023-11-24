import os,glob,sys
import sqlite3 
import argparse
from collections import defaultdict

import numpy as np
from test import single_match_query
from find_people_who_did_not_yet_start import make_email_dic
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--database_path",type=str,default="../database.db")
    parser.add_argument("--mail_dir_path",type=str,default="./mails/")    
    parser.add_argument("--target",type=int,default=135) 
    args = parser.parse_args()

    conn = sqlite3.connect(args.database_path)
    c = conn.cursor()
    c.execute("select id from user")

    all_user_ids = list(filter(lambda x:x>2,[row[0] for row in c.fetchall()]))

    did_not_finish_ids = []
    finished_nb_dic = {}

    if not os.path.exists("finished_nb_dic.npy"):
        for idUser in all_user_ids:

            idVideo = single_match_query(f"select id from video where idOwner=={idUser}",c)[0]

            c.execute(f"select id from image where idVideo=={idVideo} and nameImage like 'F0%'")

            all_annot_done = True
            finished_nb = 0
            img_ids = c.fetchall()
            print("user",idUser,"has",len(img_ids),"images to annotate")
            for img_id in img_ids:
    
                c.execute(f"select COUNT(*) from annotation where idImg=={img_id[0]} and idUser=={idUser}")

                annot_done = (c.fetchone()[0] > 0)

                all_annot_done = all_annot_done*annot_done
                finished_nb += 1*annot_done
                if not annot_done:
                    break

            if finished_nb<args.target:
                did_not_finish_ids.append(idUser)
                    
            finished_nb_dic[idUser] = finished_nb
        
        np.save("finished_nb_dic.npy",finished_nb_dic)
    
    else:
        print("Loading")
        finished_nb_dic = np.load("finished_nb_dic.npy",allow_pickle=True).item()

    center_list = []

    for idUser in finished_nb_dic:
        if finished_nb_dic[idUser] < args.target:
            idCenter = single_match_query(f"select idCenter from user where id=={idUser}",c)[0]
            center_list.append(idCenter)

            center_name = single_match_query(f"select name from center where id=={idCenter}",c)[0]
        
            print("didnotfinish",center_name,idUser,finished_nb_dic[idUser])

    name_dic = {}
    for idCenter in center_list:
        c.execute(f"select name from center where id=={idCenter}")
        name_dic[idCenter] = c.fetchone()[0]

    email_dic = make_email_dic(name_dic,args.mail_dir_path)
    
    email_list = []
    for idCenter in center_list:
        email_list.append(email_dic[idCenter])

    email_list = list(set(email_list))

    for email in email_list:
        print(email)

if __name__ == "__main__":
    main()