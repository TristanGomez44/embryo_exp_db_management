This repo contains scripts to manage the database for the experiment with embryologists where they annotate blastocysts while being assisted (or not) by a model.

To generate the database, run the following command:
```
prepare_expeembryon.py --database_path database.db --nb_of_annot_per_vid 5 --participant_nb 80
```
This will create 80 users and assign them a number of images such that each image has at least 5 biologists assigned.

To add users, use the `add_users.py` script. Arguments are detailed in the script.

To find people who did not finish annotation use the `find_people_who_did_not_finish.py`.

To find people who did not start annotations yet, use the `find_people_who_did_not_yet_start.py`.

To prepare the phase 2:
```
python3 prepare_expeembryo_phase2.py --phase_1_database_path database.db --phase_2_database_path database_phase.db
```
where `database.db` is the path to the existing database and `database_phase.db` is the path to the database for the phase 2 that will be created. Once this script is done, replace the phase 1 database with the one for phase 2. This script assign new images to each user and takes care that each user sees new images during phase 2.


