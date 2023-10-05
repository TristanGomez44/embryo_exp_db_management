import argparse
import shutil 
import glob
import sqlite3
import os,sys
import pathlib
from datetime import datetime

import numpy as np

from generate_logins_and_mails import get_name,fill_placeholders

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--mail_template_path",type=str,default="mail_template.txt")
    parser.add_argument("--email_name_path",type=str,default="email_names.csv")
    parser.add_argument("--mail_folder",type=str,default="./mails")
    args = parser.parse_args()

    email_name_csv = np.genfromtxt(args.email_name_path,delimiter=",",dtype=str,skip_header=1)
    email_name_dic= {email:name for (email,name) in email_name_csv}

    email_paths = glob.glob(os.path.join(args.mail_folder,"*"))

    with open(args.mail_template_path, 'r') as file:
        template_mail = file.read()

    date = datetime.today().strftime('%d-%m-%Y')

    print(args.mail_folder)
    new_email_folder = args.mail_folder.replace("mails",f"mails_{date}")
    os.makedirs(new_email_folder,exist_ok=True)

    for path in email_paths:

        with open(path, 'r') as file:
            mail = file.read()
        
        logins_mdp = mail.split("pour vous connecter sur le site:")[1].split("Une fois que vous avez réparti")[0].replace("\n\n","")
        participant_nb = len(logins_mdp.split("\n"))

        email_adress = os.path.basename(path).replace(".txt","")
        name = get_name(email_adress,email_name_dic)

        new_mail = fill_placeholders(template_mail,name,participant_nb,logins_mdp)
        new_mail_path = os.path.join(new_email_folder,str(email_adress) + ".txt")

        with open(new_mail_path,"w") as file:
            print(new_mail,file=file)


if __name__ == "__main__":
    main()