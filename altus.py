# # "A Toy Analysis of Mortality Rates of Acute Care Hospitals vs. VA Hospitals"
#
# First Data engineer activities are done by means of an Altus Job (cleaning and joining the datasources)
# After the data engineering activities have cleaned and joined the data sources, the data scientists can do their work. As an example, we briefly analyze various death rate statistics comparing Acute Carre hospitals (generally locally/state-funded) with VA hospitals which tends to be federally funded.
#
# ## Sample Research Question:
#
# ### "Do hospitals in states with lower per capita GDP have higher 30-day death rates, and does the result differ between state/locally-run hospitals Acute Care Hospitals and federally-run VA hospitals?"
#
# ## Data Sources:
# * Data.Medicare.Gov: https://data.medicare.gov/data/hospital-compare
# * Wikipedia: https://en.wikipedia.org/wiki/List_of_U.S._states_by_GDP_per_capita
#
# ## Disclaimers:
# * This is not a serious, rigorous study. Invalid approximations have been made and the results are merely ilustrations of a potential framework. The point is to generate graphs that arise from merging and correlating real data.
#

# ------
#


import os
import sys
import shutil
from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gsp
import sklearn.linear_model as LM
import seaborn as sns
import boto3
import cStringIO

import subprocess
import json
import time


jobid = ""
jobstatus = ""

# Make sure that output folder is non existent

s3 = boto3.resource('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
bucket = s3.Bucket('fhereygersaltus')
tmp = bucket.objects.filter(Prefix="spark/data/output").delete()

# Start Altus Job

!./runETL.sh

# Retrieve JobId of Altus Job

with open("output.txt") as json_file:
    json_data = json.load(json_file)
    jobid=json_data["jobs"][0]["jobId"]

# Idle loop until Altus Job Completed (check every 10 seconds for status)

cmd = ".local/bin/altus dataeng describe-job --job-id "+jobid
p=1

while (p<40):
  output = subprocess.check_output(cmd, shell=True)
  out = json.loads(output)
  jobstatus = out['job']['status']
  if jobstatus in ['COMPLETED', 'FAILED']:
     break
  p=p+1
  time.sleep(10)

print("The Altus Job finished with Status: "+jobstatus)


# Retrieve and merge Altus-generated result files:

client = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

part0 = cStringIO.StringIO()
client.download_fileobj('fhereygersaltus', 'spark/data/output/part-00000', part0)
part1 = cStringIO.StringIO()
client.download_fileobj('fhereygersaltus', 'spark/data/output/part-00001', part1)

part0.seek(0)
part1.seek(0)

csv = cStringIO.StringIO()
for line in part0.readlines():
  csv.write(line[1:-2]+"\n")
for line in part1.readlines():
  csv.write(line[1:-2]+"\n")

csv.seek(0)

# Creation and subsetting of dataframes:

results = pd.read_csv(csv, header=None)
results.columns = ["State", "Condition", "HospitalType","avgScore","GDP"]
results.to_csv('data.csv')

results =  results[results.GDP < 100000]     ## filter out Washington DC as a special case and outlier
results =  results[results.HospitalType != "Critical Access Hospitals"]     ## filter out Critical Access Hospitals
results.loc[:,'GDP'] /= 1000 # Divide GDP by 1000 to get $1Ks

# # AMI Mortality (Heart Attacks)

AMI_30_Death = results[results.Condition == 'Acute Myocardial Infarction (AMI) 30-Day Mortality Rate']
sns.lmplot("avgScore", "GDP", data=AMI_30_Death, col="HospitalType").set_axis_labels("30-day Death Rate", "State GDP per capita ($1k)")

# # Pneumonia Mortality

PN_30_Death = results[results.Condition == 'Pneumonia (PN) 30-Day Mortality Rate']
sns.lmplot("avgScore", "GDP", data=PN_30_Death, col="HospitalType").set_axis_labels("30-day Death Rate", "State GDP per capita ($1k)")

# # Heart Failure Mortality
HF_30_Death = results[results.Condition == 'Heart failure (HF) 30-Day Mortality Rate']
sns.lmplot("avgScore", "GDP", data=HF_30_Death, col="HospitalType").set_axis_labels("30-day Death Rate", "State GDP per capita ($1k)")

# #### Notes and Conclusions:
#
# The following results are based on a relatively small dataset (# of states in US), and are  consequently of low statistical significance.
#
# * We observe that VA hospitals have higher generally death rate variations across all three mortality groups compared to Acute Care hospitals.
# * Both hospital types generaly show a trend of lower death rates with higher per-capita GDP. But while this trend is certainly statistically significant for the Acute Care Hospitals for Heart Attack mortality and possibly also for Pneumonia-30-day mortalities, this is almost certainly not the case for the other situations. (Consider the confidence intervals.)
#
# More research would be needed to make more definite statement.
