import argparse
import shutil 
import sqlite3
import os 
import numpy as np
import secrets
import string
import pathlib,hashlib

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

def generate_logins(out_folder_path,csv_path,password_size):
    os.makedirs(out_folder_path,exist_ok=True)
    csv = np.genfromtxt(csv_path,delimiter=",",dtype=str)
    alphabet = string.ascii_letters + string.digits

    login_list = []
    sha256_passwd_list = []
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
            print("\t",login)
            
            login_list.append(login)
            
            passwd = ''.join(secrets.choice(alphabet) for i in range(password_size))

            byte_passwd = str.encode(passwd)
            sha256_passwd = hashlib.sha256(byte_passwd).hexdigest()
            sha256_passwd_list.append(sha256_passwd)

            center_list.append(login_pref)

            csv += f"{login},{passwd}\n"
        
        csv_path = pathlib.Path(out_folder_path,login_pref+".csv")

        with open(csv_path,"w") as file:
            print(csv,file=file)
    
    return login_list,sha256_passwd_list,center_list

if __name__ == "__main__":
    main()