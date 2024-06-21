FROM bitnami/spark:latest 

ENV SPARK_MODE=master

CMD ["/opt/bitnami/spark/bin/spark-class","org.apache.spark.deploy.master.Master"]

