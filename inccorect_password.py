import argparse
import sqlite3 
import glob
import os 

from generate_logins_and_mails import hash_passwd

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--database_path",type=str,default="../database.db")
    parser.add_argument("--mail_dir_path",type=str,default="./mails/")    
    args = parser.parse_args()

    conn = sqlite3.connect(args.database_path)
    c = conn.cursor()

    mail_paths = glob.glob(os.path.join(args.mail_dir_path,"*txt"))

    login_psswd_list = []

    for path in mail_paths:

        with open(path, 'r') as file:
            mail_content = file.read()

        login_passwd = mail_content.split("mot de passe\n")[1].split("\nUne fois que v")[0]

        login_passwd = login_passwd.split("\n")[:-1]

        for login_passwd in login_passwd:
            sep = " " if " " in login_passwd else ","
            login,passwd = login_passwd.split(sep)

            login_psswd_list.append((login,passwd,path))

            #if login in login_dic:
            #    raise ValueError(f"Login {login} already defined in {login_dic[login]['path']}. Stored password is {login_dic[login]['passwd']}. Current password is {passwd}.")
            #else:
            #    login_dic[login] = {}
            #    login_dic[login]["passwd"] = passwd
            #    login_dic[login]["path"] = path
    
    print("Found",len(login_psswd_list),"logins")

    for login,psswd,path in login_psswd_list:

        c.execute(f"select password from user where username=='{login}'")
        result = c.fetchone()

        if result is not None:

            actual_hashed_passwd = result[0]

            hashed_passwd = hash_passwd(psswd)

            if actual_hashed_passwd != hashed_passwd:
                print(path,login,passwd,hashed_passwd,actual_hashed_passwd)

        else:

            print(path,login,"not in database")

    print("DONE")

if __name__ == "__main__":
    main()