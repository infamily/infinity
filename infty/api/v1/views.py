from rest_framework import viewsets, generics, views

from infty.core.models import Topic, Comment, CommentSnapshot, Transaction
from infty.api.v1.serializers import *


class TopicViewSet(viewsets.ModelViewSet):

    serializer_class = TopicSerializer
    queryset = Topic.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):

    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()


