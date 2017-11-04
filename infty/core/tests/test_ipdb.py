import requests, json

from django.conf import settings

from decimal import Decimal
from test_plus.test import TestCase
from infty.core.models import (
    Topic,
    Comment,
    TopicSnapshot,
    CommentSnapshot
)

class TestChain(TestCase):

    def setUp(self):

        self.thinker = self.make_user('thinker')
        self.thinker.save()

        self.doer = self.make_user('doer')
        self.doer.save()

    def test_topic_to_blockchain(self):

        self.topic = Topic.objects.create(
            title='Improve test module',
            body='implement class that autogenerates users',
            owner=self.thinker,
        )
        try:
            self.topic.create_snapshot()
            self.topic.save()
        except Exception as e:
            print(e)

        self.assertEqual(
            TopicSnapshot.objects.filter(topic=self.topic).count(),
            1
        )

        self.assertEqual(
            settings.IPDB_APP_ID,
            '79f7f281'
        )


#   def test_comment_to_blockchain(self):
#       self.comment = Comment(
#           topic=self.topic,
#           text="""
#           - {1.5},{?0.5} for coming up with basic class structure,
#           - {?2.5} for implementation,
#           - {?3.5} for testing.

#           Here is the result so far:
#           https://github.com/wefindx/infty2.0/commit/9f096dc54f94c31eed9558eb32ef0858f51b1aec
#           """,
#           owner=self.doer
#       )
#       self.comment.save()
