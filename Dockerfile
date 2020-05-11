FROM python

COPY blockbuster.py /
RUN pip3 install matplotlib more_itertools

ENTRYPOINT ["python3", "/blockbuster.py"]
