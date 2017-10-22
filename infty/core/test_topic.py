# Create your tests here.
from test_plus.test import TestCase
from infty.core.models import Topic, Comment

class TestTopic(TestCase):

    def setUp(self):
        self.user_writer = self.make_user()

        self.topic = Topic.objects.create(
            title='This is incredible',
            body='The world is modifyable',
            owner=self.user_writer
        )

    def test_topic_values(self):
        self.assertEqual(
            self.topic.title,
            '.:en:This is incredible'
        )

    def test_body_values(self):
        self.assertEqual(
            self.topic.body,
            '.:en\nThe world is modifyable'
        )

    def test_body_values(self):
        self.assertEqual(
            self.topic.languages,
            ['en']
        )

class TestComment(TestCase):

    def setUp(self):
        self.user_writer = self.make_user()

        self.topic = Topic.objects.create(
            title='This is incredible',
            body='The world is modifyable',
            owner=self.user_writer
        )

        self.comment = Comment.objects.create(
            topic = self.topic,
            text='How is it going?',
            owner=self.user_writer,
        )

    def test_comment(self):
        self.assertEqual(
            self.comment.text,
            '.:en\nHow is it going?'
        )

    def test_languages(self):
        self.assertEqual(
            self.comment.languages,
            ['en']
        )
