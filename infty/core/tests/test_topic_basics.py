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

        self.topic2 = Topic.objects.create(
            title='.:en:This is incredible',
            body='.:en\nThe world is modifyable',
            owner=self.user_writer
        )

        self.topic2.save()


    def test_topic_values(self):
        self.assertEqual(
            self.topic.title,
            '.:en:This is incredible'
        )

    def test_topic_body_values(self):
        self.assertEqual(
            self.topic.body,
            '.:en\nThe world is modifyable'
        )

    def test_topic_lang_values(self):
        self.assertEqual(
            self.topic.languages,
            ['en']
        )

    def test_topic2_values(self):
        self.assertEqual(
            self.topic2.title,
            '.:en:This is incredible'
        )

    def test_topic2_body_values(self):
        self.assertEqual(
            self.topic2.body,
            '.:en\nThe world is modifyable'
        )

    def test_topic2_lang_values(self):
        self.assertEqual(
            self.topic2.languages,
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
            text='''.:en
{?1.5}, as we need to choose, etc.''',
            owner=self.user_writer,
        )
        self.comment.save()

    def test_comment(self):
        self.assertEqual(
            self.comment.text,
            '''.:en\n{?1.5}, as we need to choose, etc.'''
        )

    def test_languages(self):
        self.assertEqual(
            self.comment.languages,
            ['en']
        )
