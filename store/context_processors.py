from .models import Category
from logo.models import Weblogo

def menu_links(request):
    links = Category.objects.all()
    web_logo = Weblogo.objects.first()
    return dict(links=links, web_logo=web_logo)