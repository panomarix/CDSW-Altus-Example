.local/bin/altus dataeng submit-jobs \
--cluster-name fhereygers \
--jobs '{ "sparkJob": {
                "jars": [
                    "s3a://fhereygersaltus/spark/program/altus-sample-medicare-2.1.jar"
                ],
                "mainClass": "com.cloudera.altus.sample.medicare.transform",
                "applicationArguments": [
                   "s3a://fhereygersaltus/spark/data/input/",
                   "s3a://fhereygersaltus/spark/data/output/"
                ]
            }}' > output.txt
            
