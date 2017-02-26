from .models import Club, Sheet, Rock
import django_filters

class SheetFilter(django_filters.FilterSet):
    class Meta:
        model = Sheet
        fields = ['Club',]

class RockFilter(django_filters.FilterSet):
    class Meta:
        model = Rock
        fields = ['Sheet',]