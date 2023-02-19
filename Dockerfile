FROM python:3

FROM gorialis/discord.py

RUN pip3 install python-dotenv pymongo clean-text requests

RUN mkdir -p /usr/src/bot

WORKDIR /usr/src/bot

COPY . .

EXPOSE 80
CMD [ "python3", "Dynamico.py" ]