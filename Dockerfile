FROM alpine:3.7
RUN make /dbclient
CMD python /dbclient.py
