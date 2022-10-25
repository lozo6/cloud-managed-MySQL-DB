import dbm
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from faker import Faker
import uuid
import random

# stored sensitive information in a .env file
AZURE_MYSQL_HOSTNAME = os.getenv("AZURE_MYSQL_HOSTNAME")
AZURE_MYSQL_USER = os.getenv("AZURE_MYSQL_USERNAME")
AZURE_MYSQL_PASSWORD = os.getenv("AZURE_MYSQL_PASSWORD")
AZURE_MYSQL_DATABASE = os.getenv("AZURE_MYSQL_DATABASE")

connection_string_azure = f'mysql+pymysql://{AZURE_MYSQL_USER}:{AZURE_MYSQL_PASSWORD}@{AZURE_MYSQL_HOSTNAME}:3306/{AZURE_MYSQL_DATABASE}'
db = create_engine(connection_string_azure)

print(db.table_names())

fake = Faker()

fake_patients = [
    {
        #keep just the first 8 characters of the uuid
        'mrn': str(uuid.uuid4())[:8], 
        'first_name':fake.first_name(), 
        'last_name':fake.last_name(),
        'zip_code':fake.zipcode(),
        'dob':(fake.date_between(start_date='-90y', end_date='-20y')).strftime("%Y-%m-%d"),
        'gender': fake.random_element(elements=('M', 'F')),
        'contact_mobile':fake.phone_number(),
        'contact_home':fake.phone_number()
    } for x in range(50)]

df_fake_patients = pd.DataFrame(fake_patients)

df_fake_patients = df_fake_patients.drop_duplicates(subset=['mrn'])



# Creating NDC Codes
ndc_codes = pd.read_csv('https://raw.githubusercontent.com/hantswilliams/FDA_NDC_CODES/main/NDC_2022_product.csv')
ndc_codes_1k = ndc_codes.sample(n=1000, random_state=1) # random sample 1k rows
# drop duplicates from ndc_codes_1k
ndc_codes_1k = ndc_codes_1k.drop_duplicates(subset=['PRODUCTNDC'], keep='first')

# Creating CPT Codes
cpt_codes = pd.read_csv("https://gist.githubusercontent.com/lieldulev/439793dc3c5a6613b661c33d71fdd185/raw/25c3abcc5c24e640a0a5da1ee04198a824bf58fa/cpt4.csv")
cpt_codes_1k = cpt_codes.sample(n=1000, random_state=1) # random sample 1k rows
# drop duplicates from cpt_codes_1k
cpt_codes_1k = cpt_codes_1k.drop_duplicates(subset=['com.medigy.persist.reference.type.clincial.CPT.code'], keep='first')

# Creating ICD-10 Codes
icd10codes = pd.read_csv('https://raw.githubusercontent.com/Bobrovskiy/ICD-10-CSV/master/2020/diagnosis.csv')
list(icd10codes.columns)
icd10codesShort = icd10codes[['CodeWithSeparator', 'ShortDescription']] # make smaller df with columns of interest
icd10codesShort_1k = icd10codesShort.sample(n=1000) # random sample 1k rows
# drop duplicates from icd10codesShort_1k
icd10codesShort_1k = icd10codesShort_1k.drop_duplicates(subset=['CodeWithSeparator'], keep='first')

# Creating LOINC Codes
loinc_codes = pd.read_csv("data\loinc.csv")
loinc_codes_short = loinc_codes[['LOINC_NUM', 'LONG_COMMON_NAME']]
loinc_codes_1k = loinc_codes_short.sample(n=1000, random_state=1)
loinc_codes_1k = loinc_codes_1k.drop_duplicates(subset=['LOINC_NUM'], keep='first')



# Fake Patients
insertQuery = "INSERT INTO patients (mrn, first_name, last_name, zip_code, dob, gender, contact_mobile, contact_home) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

for index, row in df_fake_patients.iterrows():
    db.execute(insertQuery, (row['mrn'], row['first_name'], row['last_name'], row['zip_code'], row['dob'], row['gender'], row['contact_mobile'], row['contact_home']))
    print("inserted row: ", index)

df = pd.read_sql_query("SELECT * FROM patients", db)



# ICD-10 Codes
insertQuery = "INSERT INTO conditions (icd10_code, icd10_description) VALUES (%s, %s)"

startingRow = 0
for index, row in icd10codesShort_1k.iterrows():
    startingRow += 1
    db.execute(insertQuery, (row['CodeWithSeparator'], row['ShortDescription']))
    print("inserted row db: ", index)
    if startingRow == 100:
        break

df = pd.read_sql_query("SELECT * FROM conditions", db)


# Medications
insertQuery = "INSERT INTO medications (med_ndc, med_human_name) VALUES (%s, %s)"

startingRow = 0
for index, row in ndc_codes_1k.iterrows():
    startingRow += 1
    db.execute(insertQuery, (row['PRODUCTNDC'], row['NONPROPRIETARYNAME']))
    print("inserted row db: ", index)
    if startingRow == 100:
        break

df = pd.read_sql_query("SELECT * FROM medications", db)


# Treatments/Procedures
insertQuery = "INSERT INTO treatments_procedures (cpt_codes, treatments_procedures_desciption) VALUES (%s, %s)"

startingRow = 0
for index, row in cpt_codes_1k.iterrows():
    startingRow += 1
    db.execute(insertQuery, (row['com.medigy.persist.reference.type.clincial.CPT.code'], row['label']))
    print("inserted row db: ", index)
    if startingRow == 100:
        break

df = pd.read_sql_query("SELECT * FROM treatments_procedures", db)


# LOINC
insertQuery = "INSERT INTO social_determinants (social_determinants_description, loinc_codes) VALUES (%s, %s)"

startingRow = 0
for index, row in loinc_codes_1k.iterrows():
    startingRow += 1
    db.execute(insertQuery, (row['LONG_COMMON_NAME'], row['LOINC_NUM']))
    print("inserted row db: ", index)
    if startingRow == 100:
        break

df = pd.read_sql_query("SELECT * FROM social_determinants", db)


## Patient Conditions
df_conditions = pd.read_sql_query("SELECT icd10_code FROM conditions", db)
df_patients = pd.read_sql_query("SELECT mrn FROM patients", db)

df_patient_conditions = pd.DataFrame(columns=['mrn', 'icd10_code'])
for index, row in df_patients.iterrows():
    df_conditions_sample = df_conditions.sample(n=random.randint(1, 5))
    df_conditions_sample['mrn'] = row['mrn']
    df_patient_conditions = df_patient_conditions.append(df_conditions_sample)

print(df_patient_conditions.head(20))

insertQuery = "INSERT INTO patient_conditions (mrn, icd10_code) VALUES (%s, %s)"

for index, row in df_patient_conditions.iterrows():
    db.execute(insertQuery, (row['mrn'], row['icd10_code']))
    print("inserted row: ", index)



df_medications = pd.read_sql_query("SELECT med_ndc FROM medications", db) 
df_patients = pd.read_sql_query("SELECT mrn FROM patients", db)

df_patient_medications = pd.DataFrame(columns=['mrn', 'med_ndc'])
for index, row in df_patients.iterrows():
    numMedications = random.randint(1, 5)
    df_medications_sample = df_medications.sample(n=numMedications)
    df_medications_sample['mrn'] = row['mrn']
    df_patient_medications = df_patient_medications.append(df_medications_sample)

print(df_patient_medications.head(10))

insertQuery = "INSERT INTO patient_medications (mrn, med_ndc) VALUES (%s, %s)"

for index, row in df_patient_medications.iterrows():
    db.execute(insertQuery, (row['mrn'], row['med_ndc']))
    print("inserted row: ", index)