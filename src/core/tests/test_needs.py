from test_plus.test import TestCase

from src.core.models import (
    Topic
)


class TestNeeds(TestCase):

    def setUp(self):
        self.thinker = self.make_user('thinker')
        self.thinker.save()

        self.topic = Topic.objects.create(
            title='.:en:Improve life on Earth',
            body='.:en\nConstruct Earth Climate Adjusters',
            owner=self.thinker,
        )
        self.topic.save()

    def test_add_needs(self):
        self.topic.body = '''
.:en\nConstruct Earth Climate Adjusters.

```inf
- target: agents:construction_companies_N101
  needs:
  - name: ensure the companies have the level P110 permissions to build in the open sea
    united_nations: permission=P110 state=present
  - name: something new
    world_trade_organization: some=XXX state=present
- target: places:construction_companies_N101
  needs:
  - name: ensure the companies have high grade concrete type X123
    scoutbee_gmbh: cement=X123 state=present
- target: agents:humans
  needs:
  - name: ensure universal basic income to all
    world_economic_sustainability_organization: ubi=x001 state=present
```
        '''
        self.topic.save()

        self.assertEqual(
            self.topic.parents.count(),
            4
        )

    def test_update_needs(self):

        self.topic.body = '''
.:en\nConstruct Earth Climate Adjusters.

```inf
- target: agents:construction_companies_N101
  needs:
  - name: ensure the companies have the level P110 permissions to build in the open sea
    united_nations: permission=P110 state=present
  - name: something new
    world_trade_organization: some=XXX state=present
```
        '''
        self.topic.save()

        self.assertEqual(
            self.topic.parents.count(),
            2
        )

        self.assertEqual(
            Topic.objects.count(),
            3
        )

        self.topic.body = '''
.:en\nConstruct Earth Climate Adjusters.

```inf
- target: agents:construction_companies_N101
  needs:
  - name: ensure the companies have the level P110 permissions to build in the open sea
    united_nations: permission=P110 state=present
  - name: something new
    world_trade_organization: some=XXX state=present
- target: places:construction_companies_N101
  needs:
  - name: ensure the companies have high grade concrete type X123
    scoutbee_gmbh: cement=X123 state=present
- target: agents:humans
  needs:
  - name: ensure universal basic income to all
    world_economic_sustainability_organization: ubi=x001 state=present
```
        '''
        self.topic.save()


        self.assertEqual(
            self.topic.parents.count(),
            4
        )

        self.assertEqual(
            Topic.objects.count(),
            5
        )


        self.topic.body = '''
.:en\nConstruct Earth Climate Adjusters.
        '''
        self.topic.save()

        self.assertEqual(
            self.topic.parents.count(),
            0
        )

        self.assertEqual(
            Topic.objects.count(),
            1
        )
