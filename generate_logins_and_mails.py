import argparse
import shutil 
import sqlite3
import os 
import numpy as np
import secrets
import string
import pathlib,hashlib

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_path",type=str,default="comptes_expeembryon.csv")
    parser.add_argument("--password_size",type=int,default=10)
    parser.add_argument("--out_folder_path",type=str,default="../../expeembryons_logins/")
    args = parser.parse_args()

    generate_logins(args.out_folder_path,args.csv_path,args.password_size)

def generate_logins_and_mails(out_folder_path,csv_path,password_size):

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

    for (email,nb) in csv:
        
        login_pref = email.split("@")[1].replace(".fr","").replace(".com","")

        login_pref = prevent_duplicate(login_pref,login_pref_list)

        login_pref_list.append(login_pref)
        
        if "-" in login_pref:
            login_pref = login_pref.split("-")[1]

        csv = "login,mdp\n"

        for i in range(int(nb)):
            login = login_pref+str(i)        
            login_list.append(login)
            
            passwd = ''.join(secrets.choice(alphabet) for i in range(password_size))

            hashed_passwd = hash_passwd(passwd)
            hashed_passwd_list.append(hashed_passwd)

            center_list.append(login_pref)

            csv += f"{login},{passwd}\n"
        
        csv_path = pathlib.Path(out_folder_path,"logins",login_pref+".csv")
        with open(csv_path,"w") as file:
            print(csv,file=file)
    
        write_email(csv,out_folder_path,email)

    return login_list,hashed_passwd_list,center_list

if __name__ == "__main__":
    main()