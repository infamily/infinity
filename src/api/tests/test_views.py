# coding: utf-8
from autofixture import AutoFixture
from rest_framework.reverse import reverse, reverse_lazy
from rest_framework.test import APITestCase

from src.core.models import Topic
from src.meta.models import Type
from src.users.models import User


class TopicCreateTestCase(APITestCase):
    def setUp(self):
        super(TopicCreateTestCase, self).setUp()
        AutoFixture(Type, field_values={'is_category': True}).create(3)
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

    def test_create_topic_with_assigned_hyperlinked_categories_created(self):
        categories = [reverse('type-detail', args=(o.pk,)) for o in Type.objects.categories().all()]

        self.client.post(reverse('topic-list'), data={
            'title': '.:en:Test title',
            'body': '.:en\nTest body',
            'type': Topic.IDEA,
            'categories': categories,
        })

        instance = Topic.objects.first()
        self.assertEqual(instance.categories.count(), len(categories))

    def test_create_topic_with_assigned_categories_str_created(self):
        categories_str = sorted(Type.objects.categories().values_list('name', flat=True))

        response = self.client.post(reverse('topic-list'), data={
            'title': '.:en:Test title',
            'body': '.:en\nTest body',
            'type': Topic.IDEA,
            'categories_str': categories_str,
        })

        self.assertEqual(categories_str, sorted(response.data['categories_names']))

    def test_create_topic_hyperlinked_and_str_categories_are_merged(self):
        queryset = Type.objects.categories().order_by('id').all()
        categories_str = sorted(queryset.values_list('name', flat=True)[0:1])
        categories_obj = [reverse('type-detail', args=(o.pk,)) for o in queryset[1:]]

        response = self.client.post(reverse('topic-list'), data={
            'title': '.:en:Test title',
            'body': '.:en\nTest body',
            'type': Topic.IDEA,
            'categories': categories_obj,
            'categories_str': categories_str,
        })

        instance = Topic.objects.first()
        self.assertEqual(instance.categories.count(), len(categories_obj)+len(categories_str))
