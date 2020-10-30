FROM cimg/python:3.8.5
WORKDIR /portfolio
COPY requirements.txt requirements.txt
RUN find /portfolio -name "requirements.txt" 2>&1 | grep -v "Permission denied"
RUN pip install -r requirements.txt
RUN find /portfolio -name "requirements.txt" 2>&1 | grep -v "Permission denied"
EXPOSE 5432
RUN find /portfolio -name "requirements.txt" 2>&1 | grep -v "Permission denied"
COPY . .
RUN find /portfolio -name "requirements.txt" 2>&1 | grep -v "Permission denied"

