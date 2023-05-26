#!/usr/bin/env python3
# -*- coding: UTF 8 -*-
import configparser
import logging
import threading
import time
from datetime import datetime

import requests
import sqlalchemy
from sqlalchemy import Column, Integer
from sqlalchemy import create_engine, select
from sqlalchemy.orm import mapper

Base = sqlalchemy.orm.declarative_base()


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    status = Column(Integer)
    date = Column(Integer)
    message_id = Column(Integer)

    def __init__(self, status, date, message_id=0):
        self.status = status
        self.date = date
        self.message_id = message_id

    def _keys(self):
        return self.id

    def __eq__(self, other):
        return self._keys() == other._keys()

    def __hash__(self):
        return hash(self._keys())


class Database:
    def __init__(self, obj):
        engine = create_engine(obj, echo=False)
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        self.session = Session()
        # init db method
        # Base.metadata.create_all(engine)

        self.last_event = None

    def add_event(self, event):
        self.session.add(event)
        self.session.commit()

        self.last_event = event

    def get_last_event(self):
        if self.last_event is None:
            self.last_event = self.session.execute(select(Event).order_by(sqlalchemy.desc(Event.date))).scalar()
        return self.last_event


class ExportBot:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./config')
        log_file = config['Params']['log_file']
        logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s \
                        [%(asctime)s] %(message)s', level=logging.INFO, filename=u'%s' % log_file)
        self.chat_id = config['Telegram']['chat_id']
        self.bot_access_token = config['Telegram']['access_token']

    def public_post(self, text):
        url = f"https://api.telegram.org/bot{self.bot_access_token}/sendMessage?chat_id={self.chat_id}&text={text}"
        requests.get(url)


class Checker:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./config')
        self.delay_between_messages = int(config['Params']['delay_between_messages'])
        self.link = config['Params']['request_link']
        self.database = Database(config['Database']['Path'])
        self.bot = ExportBot()

        self.thread = threading.Thread(target=self.worker)
        self.thread.start()

    def worker(self):
        while True:
            self.process()
            time.sleep(self.delay_between_messages)

    def process(self):
        resp = requests.get(self.link, headers={"User-Agent": ""})
        prev_event = self.database.get_last_event()
        status_code = resp.status_code
        date = datetime.now()
        if prev_event is None or prev_event.status != status_code:
            if status_code == 200:
                status_emoji = "🟢"
            else:
                status_emoji = "🔴"
            event = Event(status_code, date.timestamp())
            if prev_event is None:
                time_between = "-"
            else:
                time_between = (datetime.now() - datetime.fromtimestamp(prev_event.date)).seconds
            text = (
                """ETIS: {0} ({1})
Время с прошлого состояния: {2} сек.
                """.format(status_emoji, status_code, time_between)
            )
            self.bot.public_post(text)
            self.database.add_event(event)
            logging.info("posted")
        else:
            logging.info("skip post due to same status")


if __name__ == '__main__':
    Checker()
