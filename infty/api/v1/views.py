from rest_framework.decorators import renderer_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import (
    schemas,
    response,
    renderers,
)

schema_generator = schemas.SchemaGenerator(title='Infinity API')


@api_view()
@renderer_classes([renderers.CoreJSONRenderer])
@permission_classes((IsAuthenticatedOrReadOnly,))
def schema_view(request):
    """
    Explicit schema view
    http://www.django-rest-framework.org/api-guide/schemas/#using-an-explicit-schema-view
    """
    schema = schema_generator.get_schema(request)
    return response.Response(schema)
