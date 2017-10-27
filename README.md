# This project showcases that one can start Altus ETL jobs out of a CDSW Job in a sheduled way

## Relevant Files:

* altus.py: contains the script that performs ETL with Altus first before interpreting the ETL output in Python
* runETL.sh: contains the Altus command that is being send to Altus

## Prerequisites: 

* Provide the data and spark application in S3 Buckets. The scripts currently point to:
   * s3a://fhereygersaltus/spark/data/input/
   * s3a://fhereygersaltus/spark/data/output/
   * s3a://fhereygersaltus/spark/program/altus-sample-medicare-2.1.jar
  
  You need to rename those in **altus.py** and **runETL.sh** to your buckets
  
* in Settings > Engine: Add the Project Environment parameters **AWS_ACCESS_KEY_ID** and **AWS_SECRET_ACCESS_KEY** and fill in your AWS credentials

* Install Altus Client in a terminal session (Open Workbench > Start Session > Terminal Access)

   ```
   pip install altuscli 
   pip install --upgrade altuscli
   ```
   
   You can verify whether it is installed by means of:
   
    ```
    .local/bin/altus --version
   ```
* Rename that the referenced cluster *fhereygers* in file runETL.sh to an existing cluster within Altus. Alternatively you can also adapt the script to create a cluster.

## Demo hints 
One can start a recurring job in CDSW (The Altus job finishes in ca 2 minutes)
