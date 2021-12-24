FROM ubuntu:20.04
RUN apt-get dist-upgrade
RUN apt-get update
RUN apt-get install gcc-7 g++-7 -y
RUN apt-get install gfortran-7 gfortran -y
RUN apt-get install python3 python3-pip -y
RUN DEBIAN_FRONTEND=noninteractive apt install apt-transport-https ca-certificates curl software-properties-common -y
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
RUN apt-cache policy docker-ce
RUN apt install docker-ce -y
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
COPY water_modelling/ water_modelling/
EXPOSE 5000
WORKDIR /water_modelling/server
ENV PYTHONPATH /water_modelling
CMD ["python3", "main.py"]
