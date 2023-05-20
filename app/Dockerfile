FROM python:3.10-bullseye

WORKDIR /app

COPY . .

COPY req.txt req.txt

RUN pip install -r req.txt  

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
