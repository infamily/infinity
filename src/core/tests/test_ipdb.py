import requests
import json

from test_plus.test import TestCase
from core.models import (
    Topic,
    Comment,
)
from transactions.models import (
    TopicSnapshot,
    CommentSnapshot,
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

        #self.topic.create_snapshot(blockchain=1)
        self.topic.create_snapshot(blockchain=False)
        self.topic.save()

        self.assertEqual(
            TopicSnapshot.objects.filter(topic=self.topic).count(),
            1
        )

        self.comment = Comment(
            topic=self.topic,
            text="""
            - {1.5},{?0.5} for coming up with basic class structure,
            - {?2.5} for implementation,
            - {?3.5} for testing.

            Here is the result so far:
            https://github.com/wefindx/infty2.0/commit/9f096dc54f94c31eed9558eb32ef0858f51b1aec
            """,
            owner=self.doer
        )
        self.comment.save()
        self.comment.create_snapshot(blockchain=1)
        #self.comment.create_snapshot(blockchain=False)

        self.assertEqual(
            CommentSnapshot.objects.filter(comment=self.comment).count(),
            1
        )
