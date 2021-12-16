FROM ubuntu:20.04
RUN apt-get dist-upgrade
RUN apt-get update && apt-get install -y curl
# RUN apt-get upgrade
# RUN apt-get install curl -y
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl
CMD ["sleep", "infinity"]