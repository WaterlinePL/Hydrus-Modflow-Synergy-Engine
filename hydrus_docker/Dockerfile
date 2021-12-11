FROM ubuntu:20.04
COPY hydrus .
RUN apt-get update
RUN apt-get install gfortran -y
RUN touch LEVEL_01.DIR
RUN echo "/workspace/hydrus" >> LEVEL_01.DIR
CMD ["./hydrus"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]
# use line above to debug content inside container (comment the CMD line)