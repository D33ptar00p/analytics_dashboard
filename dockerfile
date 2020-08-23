# Dockerfile - this is a comment. Delete me if you want.
FROM sheercat/fbprophet:latest
COPY . /app
WORKDIR /app
RUN apt-get update -y
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
