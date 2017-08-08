# PERMISSIONS
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

# STANDARD VIEWS
from rest_framework.views import APIView
from rest_framework.response import Response

@permission_classes((AllowAny, ))
class ExampleView(APIView):
    def get(self, request, *args, **kwargs):
        example = request.GET.dict()
        return Response(example)

# MODEL SERIALIZERS
from rest_framework import serializers
from rest_framework import viewsets, generics, views

from infty.core.models import Topic

class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = [
            'title',
            'body'
        ]

class TopicListView(generics.ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        example = request.GET.dict()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
