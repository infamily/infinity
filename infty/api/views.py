from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.renderers import CoreJSONRenderer, BrowsableAPIRenderer
from rest_framework import (
    schemas,
    response,
)

schema_generator = schemas.SchemaGenerator(title='Infinity API')


class SchemaView(APIView):
    renderer_classes = (
        CoreJSONRenderer,
        BrowsableAPIRenderer,
    )

    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request):
        schema = schema_generator.get_schema(request)
        return response.Response(schema)
