FROM ubuntu

LABEL maintainer="rdevera6@my.bcit.ca"

RUN apt update -y && \
    apt -y upgrade && \
    apt install -y python3 python3-pip
    
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
