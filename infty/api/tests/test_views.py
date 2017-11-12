# coding: utf-8
from autofixture import AutoFixture
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from infty.core.models import Topic
from infty.users.models import User


class TopicCreateTestCase(APITestCase):
    def setUp(self):
        self.user = AutoFixture(User).create(1)[0]
        self.client.force_login(self.user)

    def test_create_topic_response_201(self):
        rv = self.client.post(reverse('topic-list'), data={
            'title': 'Test title',
            'body': 'Test body',
            'type': Topic.IDEA,
        })

        self.assertEqual(rv.status_code, 201)

    def test_create_topic_instance_fields_ok(self):
        self.client.post(reverse('topic-list'), data={
            'title': '.:en:Test title',
            'body': '.:en\nTest body',
            'type': Topic.IDEA,
        })

        instance = Topic.objects.first()

        self.assertEqual(instance.title, '.:en:Test title')
        self.assertEqual(instance.body, '.:en\nTest body')
        self.assertEqual(instance.type, Topic.IDEA)
