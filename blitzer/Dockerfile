FROM python:3-alpine
WORKDIR /blitzer
COPY ./collector.py .
RUN pip install -U pip prometheus-client pydantic requests
RUN pwd
EXPOSE 49999
ENTRYPOINT ["/usr/local/bin/python"]
CMD ["./collector.py"]
