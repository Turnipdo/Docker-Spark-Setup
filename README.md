# Docker-Spark-Setup :atom:
Setting up a Spark cluster in a Docker environment for improved repeatability and reliability. This project includes a simple transformation on a dataset containing approximately 31 million rows.

## Requirements :basecamp:
* `Docker-Desktop`
* `Pyspark`
* `Python`
* `VScode`

## Instructions :page_with_curl:
### File creations + All the scripts needed in your directory

* You want to start by creating a project directory anywhere you'd like, for me this is the location and I also named it :file_folder:Spark-Cluster-Setup:
`C:\Users\Username\Projects\Spark-Cluster-Setup`<br><br>
* You will also need to create another subfolder inside this directory called :file_folder:scripts which will hold the python scripts we will be executing the data transformations: `C:\Users\Username\Projects\Spark-Cluster-Setup\scripts`<br><br>
* I've also downloaded a data set (roughly around 31 million rows) from [Kaggle](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml), the one I used was `LI-Medium_Trans.csv`. I created another subfolder inside my scripts folder, named it :file_folder:LI-Medium_Trans_Folder and dumped the csv file in there. The hierarchy looks like this: `C:\Users\Username\Projects\Spark-Cluster-Setup\scripts\LI-Medium_Trans_Folder\LI-Medium_Trans.csv`<br><br> 
* Once all of this is created, navigate back to the :file_folder:Spark-Cluster-Setup folder and if you're already navigating using the temrinal window then great, if not right-click and click on `Open Terminal` and type the following command to open VScode:<br>

```bash
PS C:\Users\Username\Projects\Spark-Cluster-Setup> code .
```
* Once VScode is opened, you first need to create a `Dockerfile` inside the same directory, we will use the pre-built image for spark offered by bitnami which makes this setup super easy and understandable.
  * The following code essentially just pulls the latest image provided by bitnami.
  * Set the environment variable and specifying that the Spark instance will run as the mater node.
  * From the `/opt/bitnami/spark/bin/spark-class` path, use the command `org.apache.spark.deploy.master.Master` command to start the Spark master.
```Dockerfile
FROM bitnami/spark:latest

ENV SPARK_MODE=master

CMD ["/opt/bitnami/spark/bin/spark-class","org.apache.spark.deploy.master.Master"]
```
* We have to create a `docker-compose.yaml` file to build a container for the master and all of its worker nodes, along with their configurations.
  * For the spark master you will see that we've omitted the `image: bitnami/spark:latest`, this is because we have a `build: .` which indicates to build the image from the `Dockerfile` previously mentioned into the current directory.
  * For each and every node, there must be an associated container, and all the worker nodes depend on on the spark-master.
  * Alot of the configs in the `environment` section is basically from the [documentation](https://spark.apache.org/docs/latest/spark-standalone.html) provided by spark.
  * I've basically configured the master and worker nodes taking into consideration the limitations of my computer's performance (6 cores and 16 GB of RAM)
  * You can also find the default `SPARK_MASTER_URL` and more information on bitnami's spark image [here](https://hub.docker.com/r/bitnami/spark).
  * I added a volumes section in the `docker-compose.yml` file for both the Spark master and every worker node. This is crucial because it mounts the :file_folder:scripts folder where all your `.py` scripts are located. This ensures that both the master and worker nodes know where to find and execute the Python scripts.
```yaml
version: '3'
services:
  spark-master:
    build: .
    container_name: spark-master
    hostname: spark-master
    environment:
      - SPARK_MODE=master
      - SPARK_MASTER_PORT=7077
      - SPARK_MASTER_WEBUI_PORT=8080
      - SPARK_DAEMON_MEMORY=3g
    volumes:
      - ./scripts:/scripts
    ports:
      - "8080:8080"
      - "7077:7077"

  spark-worker-1:
    image: bitnami/spark:latest
    container_name: spark-worker-1
    hostname: spark-worker-1
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_WEBUI_PORT=8081
      - SPARK_WORKER_CORES=1
      - SPARK_WORKER_MEMORY=3G
    volumes:
      - ./scripts:/scripts
    depends_on:
      - spark-master
    ports:
      - "8081:8081"

  spark-worker-2:
    image: bitnami/spark:latest
    container_name: spark-worker-2
    hostname: spark-worker-2
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_WEBUI_PORT=8082
      - SPARK_WORKER_CORES=1
      - SPARK_WORKER_MEMORY=3G
    volumes:
      - ./scripts:/scripts
    depends_on:
      - spark-master
    ports:
      - "8082:8082"

  spark-worker-3:
    image: bitnami/spark:latest
    container_name: spark-worker-3
    hostname: spark-worker-3
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_WEBUI_PORT=8083
      - SPARK_WORKER_CORES=1
      - SPARK_WORKER_MEMORY=3G
    volumes:
      - ./scripts:/scripts
    depends_on:
      - spark-master
    ports:
      - "8083:8083"
```
* You can also use the following python script (I called it `test_script.py`) that will start the spark session, read the csv file and do a simple average calculation based on the Payment Formats in the csv file.
  * I used the time module because I wanted to see how much time it takes to process 31 million rows of data (first time doing this and i'm also a noob still so I was curious)
  * You can honestly omit the entire schema part because it worked well even if I didn't use the schema, I just wanted to try it out and practice so, apologies in advance.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import time

spark = SparkSession.builder \
    .appName("DataRead&Process") \
    .getOrCreate()

schema = StructType([
    StructField("Timestamp", StringType(), True),
    StructField("From Bank", IntegerType(), True),
    StructField("From Account", StringType(), True),
    StructField("To Bank", IntegerType(), True),
    StructField("To Account", StringType(), True),
    StructField("Amount Received", DoubleType(), True),
    StructField("Receiving Currency", StringType(), True),
    StructField("Amount Paid", DoubleType(), True),
    StructField("Payment Currency", StringType(), True),
    StructField("Payment Format", StringType(), True)
])


start_time_load = time.time()
df = spark.read.csv("/scripts/LI-Medium_Trans_Folder/LI-Medium_Trans.csv", header=True, schema=schema)
selected_df = df.select("Amount Paid", "Payment Format")
end_time_load = time.time()

start_time_transform = time.time()
avg_amt_paid = selected_df.groupBy("Payment Format").agg(avg("Amount Paid").alias("Avg Amount Paid"))
avg_amt_paid.show(50, truncate=False)
end_time_transform = time.time()

load_time = end_time_load - start_time_load
transform_time = end_time_transform - start_time_transform

print(f"time taken to load data: {load_time}")
print(f"time taken to transform data: {transform_time}")
```
### Building the Docker image and running the python script!
* After you have all those file setup, make sure everything is saved and we will not build the Docker Image.<br><br>
* Open up Docker-Desktop, ensure Docker engine is running, open up a new Terminal window in your VScode and use the following command
```bash
$ docker-compose up --build
[+] Building 0.1s (5/5) FINISHED                                                                                          docker:default
 => [spark-master internal] load build definition from Dockerfile                                                                   0.0s
 => => transferring dockerfile: 180B                                                                                                0.0s
 => [spark-master internal] load metadata for docker.io/bitnami/spark:latest                                                        0.0s
 => [spark-master internal] load .dockerignore                                                                                      0.0s
 => => transferring context: 2B                                                                                                     0.0s
 => CACHED [spark-master 1/1] FROM docker.io/bitnami/spark:latest                                                                   0.0s
 => [spark-master] exporting to image                                                                                               0.0s
 => => exporting layers                                                                                                             0.0s
 => => writing image sha256:173aa9b7301ad4cf28f237ef5b606aeab444fd9ff60248a84cb44306fd456c12                                        0.0s
 => => naming to docker.io/library/spark-cluster-setup-spark-master                                                                 0.0s
[+] Running 5/5
 ✔ Network spark-cluster-setup_default  Created                                                                                     0.0s 
 ✔ Container spark-master               Created                                                                                     0.1s 
 ✔ Container spark-worker-3             Created                                                                                     0.1s 
 ✔ Container spark-worker-1             Created                                                                                     0.1s 
 ✔ Container spark-worker-2             Created        
```
* You've succesfully setup your spark-cluster using Docker, you can navigate to `http://localhost:8080/home` to verify if the master and all of your worker nodes are up and running by changing 8080 to 8081, 8082, etc.<br><br>
* Open up a new terminal in VScode, and use the following commands, you'll have a long list when you execute the python script so I've just shortened it so you have an idea how it looks:
```bash
$ docker exec -it spark-master bash
I have no name!@spark-master:/opt/bitnami/spark$

$ cd /scripts
I have no name!@spark-master:/scripts$

$ spark-submit --master spark://spark-master:7077 /scripts/test_script.py
24/06/21 08:04:47 INFO SparkContext: Running Spark version 3.5.1
24/06/21 08:04:47 INFO SparkContext: OS info Linux, 5.15.153.1-microsoft-standard-WSL2, amd64
24/06/21 08:04:47 INFO SparkContext: Java version 17.0.11
24/06/21 08:04:47 INFO ResourceUtils: ==============================================================
24/06/21 08:04:47 INFO ResourceUtils: No custom resources configured for spark.driver.
24/06/21 08:04:47 INFO ResourceUtils: ==============================================================
...
24/06/21 08:05:02 INFO TaskSetManager: Starting task 3.0 in stage 0.0 (TID 3) (172.18.0.5, executor 0, partition 3, PROCESS_LOCAL, 8229 bytes)
24/06/21 08:05:02 INFO TaskSetManager: Finished task 0.0 in stage 0.0 (TID 0) in 6492 ms on 172.18.0.5 (executor 0) (1/23)
24/06/21 08:05:02 INFO TaskSetManager: Starting task 4.0 in stage 0.0 (TID 4) (172.18.0.3, executor 1, partition 4, PROCESS_LOCAL, 8229 bytes)
24/06/21 08:05:02 INFO TaskSetManager: Finished task 1.0 in stage 0.0 (TID 1) in 6755 ms on 172.18.0.3 (executor 1) (2/23)
24/06/21 08:05:02 INFO TaskSetManager: Starting task 5.0 in stage 0.0 (TID 5) (172.18.0.4, executor 2, partition 5, PROCESS_LOCAL, 8229 bytes)
...
24/06/21 08:05:23 INFO TaskSetManager: Finished task 22.0 in stage 0.0 (TID 22) in 675 ms on 172.18.0.4 (executor 2) (22/23)
24/06/21 08:05:24 INFO TaskSetManager: Finished task 20.0 in stage 0.0 (TID 20) in 3575 ms on 172.18.0.3 (executor 1) (23/23)
24/06/21 08:05:24 INFO TaskSchedulerImpl: Removed TaskSet 0.0, whose tasks have all completed, from pool
...
+--------------+--------------------+
|Payment Format|Avg Amount Paid     |
+--------------+--------------------+
|ACH           |9045817.639857756   |
|Credit Card   |74801.77192402656   |
|Reinvestment  |2456738.869398785   |
|Cheque        |7171603.898055333   |
|Cash          |1.1868686948102372E7|
|Wire          |4603325.2566971695  |
|Bitcoin       |63.419871884172125  |
+--------------+--------------------+

time taken to load data: 4.0996832847595215
time taken to transform data: 31.357645511627197
...
```
* I know it should only be two floating points for currency but please spare me for now :bowtie:<br><br>
* If you want to stop the containers, all you have to do is use the following command:
```bash
$ exit bash
exit
bash: exit: bash: numeric argument required

$ docker compose down
[+] Running 5/5
 ✔ Container spark-worker-1             Removed                                                                                                                                                                                                                                                      10.7s 
 ✔ Container spark-worker-2             Removed                                                                                                                                                                                                                                                      11.0s 
 ✔ Container spark-worker-3             Removed                                                                                                                                                                                                                                                      10.8s 
 ✔ Container spark-master               Removed                                                                                                                                                                                                                                                       0.9s 
 ✔ Network spark-cluster-setup_default  Removed  
```
* From next time on, if you want to start the container again it's simply just:
```bash
$ docker compose up
[+] Running 5/5
 ✔ Network spark-cluster-setup_default  Created                                                                                                                                                                                                                                                       0.0s 
 ✔ Container spark-master               Created                                                                                                                                                                                                                                                       0.0s 
 ✔ Container spark-worker-2             Created                                                                                                                                                                                                                                                       0.1s 
 ✔ Container spark-worker-3             Created                                                                                                                                                                                                                                                       0.1s 
 ✔ Container spark-worker-1             Created                                                                                                                                                                                                                                                       0.1s 
Attaching to spark-master, spark-worker-1, spark-worker-2, spark-worker-3
```
## Conclusion :electron:
We've not only learned how to set up a standalone Spark cluster, but also optimized it for repeatability and reliability by leveraging Docker containerization. While the bitnami pre-built image restricts extensive customization options, it allowed me to quickly establish and gain experience with this powerful big data transformation tool.
