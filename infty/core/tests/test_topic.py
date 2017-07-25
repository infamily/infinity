# Create your tests here.
from test_plus.test import TestCase
from infty.core.models import Topic, Comment

class TestTopic(TestCase):

    def setUp(self):

        # Let's say we have a user 'thinker'..
        thinker = self.make_user('Thinker')

        # ..who writes a post:
        self.topic = Topic.objects.create(
            title='Improve test module',
            body='implement class that autogenerates users',
            owner=thinker,
        )

        # Then, we have a user 'doer'..
        doer = self.make_user('doer')

        # ..who creates a comment on it
        # with past time expenses, declared work result, 
        # and estimates of future time expenses.
        self.comment = Comment(
            topic=self.topic,
            text="""
            {1.5},{?0.5} for coming up with
            basic class structure, and {?2.5} for
            implementation, and {?3.5} for testing.

            Here is the result so far:
            https://github.com/wefindx/infty2.0/commit/9f096dc54f94c31eed9558eb32ef0858f51b1aec
            """
        )

    def test_comment_values(self):
        parsed_claimed_hours = 0.0 # 1.5
        parsed_assumed_hours = 0.5+2.5+3.5

        self.assertEqual(
            self.comment.claimed_hours,
            parsed_claimed_hours
        )

    def test_topic_values(self):
        self.assertEqual(
            'Hello',
            'Hello'
        )
