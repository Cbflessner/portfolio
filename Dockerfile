FROM cimg/python:3.8.5
WORKDIR /portfolio
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5432