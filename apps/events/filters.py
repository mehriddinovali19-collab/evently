import django_filters
from django.utils import timezone
from .models import Event


class EventFilter(django_filters.FilterSet):
    date_from = django_filters.DateTimeFilter(field_name='start_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='start_at', lookup_expr='lte')
    status = django_filters.ChoiceFilter(choices= Event.Status.choices)
    event_type = django_filters.ChoiceFilter(choices=Event.EventType.choices)
    upcoming = django_filters.BooleanFilter(method='filter_upcoming')

    class Meta:
        model = Event
        fields = ['status', 'event_type', 'date_from', 'date_to', 'upcoming']

    def filter_upcoming(self, queryset, name, value):
        if value:
            return queryset.filter(start_at__gt= timezone.now())
        return queryset