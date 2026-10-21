from rest_framework.decorators import api_view
from rest_framework.response import Response

DEMO_PROJECTS = [
    {
        'id': 'atlas', 'name': 'Atlas Workspace', 'type': 'PRODUCT', 'group': 'Product',
        'category': 'Productivity', 'status': 'In progress', 'statusKey': 'progress', 'updated': '2h ago',
        'description': 'A calmer command center for teams to plan, align, and move meaningful work forward.',
        'tech': ['AngularJS', 'Django', 'PostgreSQL'], 'theme': 'lavender', 'symbol': 'A', 'coverLabel': 'PLAN WITH CLARITY',
    },
    {
        'id': 'signal', 'name': 'Signal Metrics', 'type': 'PLATFORM', 'group': 'Platform',
        'category': 'Data & analytics', 'status': 'Live', 'statusKey': 'live', 'updated': 'Yesterday',
        'description': 'Turn product signals into a focused view of what is changing and why it matters.',
        'tech': ['FastAPI', 'MongoDB', 'Python'], 'theme': 'peach', 'symbol': 'S', 'coverLabel': 'FIND THE SIGNAL',
    },
    {
        'id': 'fieldnotes', 'name': 'Fieldnotes', 'type': 'EXPERIMENT', 'group': 'Experiment',
        'category': 'Knowledge', 'status': 'In progress', 'statusKey': 'progress', 'updated': '3 days ago',
        'description': 'A lightweight research library that keeps observations connected to decisions.',
        'tech': ['AngularJS', 'FastAPI', 'MongoDB'], 'theme': 'mint', 'symbol': 'F', 'coverLabel': 'NOTICE MORE',
    },
]

@api_view(['GET'])
def health(_request):
    return Response({'service': 'django-portfolio-api', 'status': 'ok'})

@api_view(['GET'])
def projects(_request):
    return Response(DEMO_PROJECTS)
