# Create your tests here.
from django.test import TestCase
from infty.core.models import Topic

class TestTopic(TestCase):

    def setUp(self):
        self.user_writer = self.make_user()
        self.user_commentator = self.make_user()

        self.topic = Topic.objects.create(
            title='Hello',
            body='World',
        )

    def test_topic_values(self):
        self.assertEqual(
            self.topic.title,
            'Hello'
        )
