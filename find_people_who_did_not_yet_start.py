import os,glob
import sqlite3 
import argparse
from collections import defaultdict

import numpy as np

def make_email_dic(name_dic,mail_dir_path):

    pattern = os.path.join(mail_dir_path,"*txt")
    mail_file_paths = glob.glob(pattern)

    email_dic = {}

    for idCenter in name_dic:

        name = name_dic[idCenter]

        for path in mail_file_paths:

            with open(path, 'r') as file:
                mail = file.read()

            if name in mail:
                email_dic[idCenter] = os.path.basename(path).replace(".txt","")

    return email_dic

def test(missing_nb,name_dic,didnot_start_dic,c):

    for idCenter in missing_nb:

        for idUser in didnot_start_dic[idCenter]:
            c.execute(f"select COUNT(*) from annotation where idUser='{idUser}'")
            count = c.fetchone()[0]
            assert count == 0,f'{idCenter},{idUser},{count}'

            c.execute(f"select idCenter from user where id='{idUser}'")
            found_idCenter = c.fetchone()[0]
            assert found_idCenter == idCenter,f'{idCenter},{idUser},{found_idCenter}'

        c.execute(f"select name from center where id=={idCenter}")
        found_name = c.fetchone()[0]

        assert found_name == name_dic[idCenter],f'{idCenter},{name_dic[idCenter]},{found_idCenter}'

    print("TEST OK")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--database_path",type=str,default="../database.db")
    parser.add_argument("--mail_dir_path",type=str,default="./mails/")    
    args = parser.parse_args()

    conn = sqlite3.connect(args.database_path)
    c = conn.cursor()
    c.execute("select id from user")

    all_user_ids = [row[0] for row in c.fetchall()]

    c.execute("select DISTINCT(idUser) from annotation")
    users_who_started = [row[0] for row in c.fetchall()]

    users_who_didnot_start = list(set(all_user_ids) - set(users_who_started))

    missing_nb = defaultdict(lambda:0)
    didnot_start_dic = defaultdict(list)

    for idUser in users_who_didnot_start:
        c.execute(f"select idCenter from user where id=={idUser}")
        idCenter = c.fetchone()[0]
        
        missing_nb[idCenter] += 1
        didnot_start_dic[idCenter].append(idUser)

    name_dic = {}
    for idCenter in missing_nb:

        c.execute(f"select name from center where id=={idCenter}")
        name_dic[idCenter] = c.fetchone()[0]

    email_dic = make_email_dic(name_dic,args.mail_dir_path)

    for idCenter in missing_nb:
        print(email_dic[idCenter])

    test(missing_nb,name_dic,didnot_start_dic,c)


if __name__ == "__main__":
    main()