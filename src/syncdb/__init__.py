import logging

from celery import shared_task
from pymongo import MongoClient
from constance import config


logger = logging.getLogger(__name__)


@shared_task
def update_syncdb_task(table, data):

    db_client = MongoClient(config.DATA_SYNC_SERVER)
    db = db_client[config.DATA_SYNC_DB]

    location = data.get('-')

    if location:

        db[table].update(
            {'-': location}, {'$set': data}, upsert=True)


def update_syncdb_async(*args):
    return update_syncdb_task.apply_async(args)
