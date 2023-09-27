import argparse
import shutil 
import sqlite3
import os 
import numpy as np
import secrets
import string
import pathlib,hashlib

def write_email(logins_csv,out_folder_path,email,mail_template_path,email_name_path,participant_nb):

    email_name_csv = np.genfromtxt(email_name_path,delimiter=",",dtype=str,skip_header=1)
    email_name_dic= {email:name for (email,name) in email_name_csv}

    with open(mail_template_path, 'r') as file:
        mail = file.read()

    name = list(email.split(".")[0])
    
    if email in email_name_dic:
        name = email_name_dic[email]
    else:
        name[0] = str.capitalize(name[0])
        name = "".join(name)

    mail = mail.replace("{name}",name)
    mail = mail.replace("{participant_nb}",participant_nb)
    mail = mail.replace("{logins_mdps}",logins_csv)

    with open(out_folder_path / "mails" / (str(email) + ".txt"),"w") as file:
        print(mail,file=file)

def hash_passwd(passwd):
    byte_passwd = str.encode(passwd)
    hashed_passwd = hashlib.sha256(byte_passwd).hexdigest()
    return hashed_passwd

def prevent_duplicate(login_pref,login_pref_list):
    if login_pref in login_pref_list:
        i = 0
        while login_pref+str(i)+"_" in login_pref_list:
            i += 1

        login_pref += str(i)+"_"

    return login_pref 

def generate_logins_and_mails(out_folder_path,csv_path,password_size,mail_template_path,email_name_path,participant_target_nb):

    out_folder_path = pathlib.Path(out_folder_path)
    os.makedirs(out_folder_path,exist_ok=True)
    os.makedirs(out_folder_path / "logins",exist_ok=True)
    os.makedirs(out_folder_path / "mails",exist_ok=True)

    csv = np.genfromtxt(csv_path,delimiter=",",dtype=str)
    alphabet = string.ascii_letters + string.digits

    login_list = []
    hashed_passwd_list = []
    center_list = []

    login_pref_list = []

    actual_participant_nb = csv[:,1].astype(int).sum()
    missing_participant_nb = participant_target_nb - actual_participant_nb
    if missing_participant_nb>0:
        supp_row = np.array([["supp.lementary@default.fr",str(missing_participant_nb)]],dtype=str)
        csv = np.concatenate((csv,supp_row),axis=0)

    for (email,participant_nb) in csv:
        
        login_pref = email.split("@")[1].replace(".fr","").replace(".com","")

        login_pref = prevent_duplicate(login_pref,login_pref_list)

        login_pref_list.append(login_pref)
        
        if "-" in login_pref:
            login_pref = login_pref.split("-")[1]

        logins_csv = "identifiant,mot de passe\n"

        for i in range(int(participant_nb)):
            login = login_pref+str(i)        
            login_list.append(login)
            
            passwd = ''.join(secrets.choice(alphabet) for i in range(password_size))

            hashed_passwd = hash_passwd(passwd)
            hashed_passwd_list.append(hashed_passwd)

            center_list.append(login_pref)

            logins_csv += f"{login},{passwd}"

            if i < int(participant_nb) - 1:
                logins_csv += "\n"
        
        csv_path = pathlib.Path(out_folder_path,"logins",login_pref+".csv")
        with open(csv_path,"w") as file:
            print(logins_csv,file=file)
    
        write_email(logins_csv,out_folder_path,email,mail_template_path,email_name_path,participant_nb)

    return login_list,hashed_passwd_list,center_list

if __name__ == "__main__":
    main()