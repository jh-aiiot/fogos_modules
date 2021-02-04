FROM ubuntu: 18.04
RUN make /dbclient
CMD python /dbclient.py
