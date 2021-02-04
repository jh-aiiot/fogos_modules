FROM alpine:3.7
COPY . /ResourceManager
RUN make /ResourceManager
CMD python /ResourceManager.py
