FROM ubuntu:18.04
COPY . /ResourceManager
RUN make /ResourceManager
CMD python /ResourceManager.py
