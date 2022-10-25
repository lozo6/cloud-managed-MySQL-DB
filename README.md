# cloud-managed-MySQL-DB
HHA 504 Assignment 6

## Assignment Details
1. Create a cloud-managed MySQL DB on either Azure or GCP

2. Create a new database inside of that mysql instance called patient_portal  

3. Create a python script called (sql_table_creation.py) that creates the following tables inside of patient_portal: patients, medications, treatments_procedures, conditions, and social determinants. Be sure to use a .env file to hide your login credentials 

4. Create a python script called (sql_dummy_data.py) using python and send some dummy data into each of the tables. Please see notes for ideas related to dummy data. 

5. Create an ERD for your DB design using MySQL Work Bench. You must have at least two foreignKeys representing a relationship between at least 2 tables. 

6. Github docs to include: 
- a python script that contains the SQL code to create db (sql_table_creation.py) 
- a python script that contains code to insert in some dummy data (sql_dummy_data.py) 
- a readme file that describes a) where you setup the mySQL db, b) any issues you ran into 
- a images folder that contains: 
    - screen shot of a ERD of your proposed setup (use either popSQL or mysql work bench) 
    - screen shots of you connected to the sql server, performing the following queries: 
        - Query1: show databases (e.g., show databases;) 
        - Query2: all of the tables from your database (e.g., show tables;)  
        - Query3: select * from patient_portal.medications 
        - Query4: select * from patient_portal.treatment_procedures
        - Query5: select * from patient_portal.conditions

Be CREATE with your dummy data and find examples that are from real-world codexes: 
Medications: NDC codes
Treatments/Procedures: CPT 
Conditions: ICD10 codes
Social_Determinants: LOINC codes 

Resources to pull some test data: 
NDC: https://dailymed.nlm.nih.gov/dailymed/index.cfm 
CPT: https://www.aapc.com/codes/cpt-codes-range/
ICD: https://icdcodelookup.com/icd-10/codes
LOINC: https://www.findacode.com/loinc/LG41762-2--socialdeterminantsofhealth.html

REAL CPT Values that are older: https://gist.github.com/lieldulev/439793dc3c5a6613b661c33d71fdd185

# How to set up


## You will need to use a `.env` file with this information to utilize dotenv module

```yaml
AZURE_MYSQL_HOSTNAME = "insert here"
AZURE_MYSQL_USERNAME = "insert here"
AZURE_MYSQL_PASSWORD = "insert here"
AZURE_MYSQL_DATABASE = "insert here"
```


## How to set up Virtual Cloud Environment

I will be using Microsoft Azure for the assignment but this can also be done using Google Cloud Platform

Create a Virtual Machine (VM) with minimum requirements for installing MySQL in Linux environment (Ubuntu)

1. Use sudo apt-get update and sudo apt install python3-pip # to install all dependencies in Ubuntu OS

2. Use sudo apt install mysql-server mysql-client # to install MySQL in Ubuntu OS

3. Use sudo mysql # to login using administrative privileges

4. To add administrative users to Virtual Machine: CREATE USER 'lozo'@'%' IDENTIFIED BY 'lozoAHI2023!';

    SELECT user FROM mysql.user; # shows a list of all users in Ubuntu OS

    GRANT ALL PRIVILEGES ON *.* TO 'lozo'@'%'; # grants all admin privileges to user

    To test use '$ mysql -u lozo -p' and enter the password: lozoAHI2023!

5. Please Add Inbound Port Rule to allow port '3306' to connect to help MySQL server

6. Use sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf and change 'bind_address' from 127.0.0.1 to 0.0.0.0

7. Please refer to main.py for adding data into MySQL