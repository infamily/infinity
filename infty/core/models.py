from decimal import Decimal
from re import finditer

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _

from infty.generic.models import GenericTranslationModel
from infty.users.models import User, CryptoKeypair
from infty.transactions.mixins import (TopicTransactionMixin,
                                       CommentTransactionMixin)


class Topic(TopicTransactionMixin, GenericTranslationModel):
    """
    Y: Main content type, to include fields of all infty types.

    Note: 'STEP' is missing intentionally. 'TASK' and 'STEP' are
    redundant, and in the choice, which one to get rid of, 'STEP'
    made more sense to remove, because people have theories of HTN
    (hierarchical task networks), and 'TASK' is understood as 'STEP'
    by AI planning community. Also 'TASK' is much more tangible thing
    to start with for people. We'll introduce the fields of 'STEP'
    (e.g., planning I/O, https://github.com/wefindx/StepIO) later.

    Note: order of languages is preserved, in the order of input.
    """
    NEED = 0  # A condition
    GOAL = 1  # Set of conditions
    IDEA = 2  # A transformation
    PLAN = 3  # Instance of Idea(s)
    STEP = 4  # Decomposition of plan
    TASK = 5  # Terminal step (action).

    TOPIC_TYPES = [
        (NEED, _('Need')),
        (GOAL, _('Goal')),
        (IDEA, _('Idea')),
        (PLAN, _('Plan')),
        (STEP, _('Step')),
        (TASK, _('Task')),
    ]

    type = models.PositiveSmallIntegerField(TOPIC_TYPES, default=TASK)
    categories = models.ManyToManyField(
        'meta.Type', related_name='topic_categories', blank=True)
    title = models.TextField()
    body = models.TextField(null=True, blank=True)

    owner = models.ForeignKey(User)
    editors = models.ManyToManyField(
        User, related_name='topic_editors', blank=True)
    parents = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='parent_topics')

    blockchain = models.PositiveSmallIntegerField(
        CryptoKeypair.KEY_TYPES, default=False)

    is_draft = models.BooleanField(default=False)

    source = models.TextField(null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        return '[{}] {}'.format(
            dict(self.TOPIC_TYPES).get(self.type), self.title)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.blockchain:
            self.create_snapshot(blockchain=self.blockchain)

    class Meta:
        translation_fields = (
            ('title', True),
            ('body', False),
        )
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        ordering = ('-pk', )


class Comment(CommentTransactionMixin, GenericTranslationModel):
    """
    X: Comments are the place to discuss and claim time and things.

    Note: the reason why we need a separate model for Comment,
    is because comments should not have multiple editors.

    Note: order of languages is preserved, in the order of input.
    """
    topic = models.ForeignKey(Topic)
    text = models.TextField()

    claimed_hours = models.DecimalField(
        default=0., decimal_places=8, max_digits=20)
    assumed_hours = models.DecimalField(
        default=0., decimal_places=8, max_digits=20)

    owner = models.ForeignKey(User)
    blockchain = models.PositiveSmallIntegerField(
        CryptoKeypair.KEY_TYPES, default=False)

    parent = models.ForeignKey('self', null=True, blank=True)

    source = models.TextField(null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def set_hours(self):

        parsed = self.parse_hours(self.text)

        self.claimed_hours = parsed['claimed_hours']
        self.assumed_hours = parsed['assumed_hours']

    def parse_hours(self, text):
        """
        Given text, e.g., comment text, parses the
        claimed_hours and assumed_hours.
        """

        claimed_hours = Decimal(0.0)
        assumed_hours = Decimal(0.0)

        for m in finditer(r'\{([^}]+)\}', text):
            token = m.group(1)
            if token:
                if token[0] == '?':
                    try:
                        hours = float(token[1:])
                        assumed_hours += Decimal(hours)
                    except Exception:
                        pass
                else:
                    try:
                        hours = float(token)
                        claimed_hours += Decimal(hours)
                    except Exception:
                        pass
        return {
            'claimed_hours': claimed_hours,
            'assumed_hours': assumed_hours,
        }

    def __str__(self):
        return "Comment for {}".format(self.topic)

    def save(self, *args, **kwargs):
        self.proceed_interaction()
        super().save(*args, **kwargs)
        if self.blockchain:
            self.create_snapshot(blockchain=self.blockchain)

    class Meta:
        translation_fields = (('text', False), )
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
