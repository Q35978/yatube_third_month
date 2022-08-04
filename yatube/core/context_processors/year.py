from django.utils import timezone


def year(request):
    today_year = timezone.now().year
    return {'year': today_year}
