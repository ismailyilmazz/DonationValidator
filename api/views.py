from rest_framework import viewsets
from need.models import Need
from .serializers import NeedSerializer
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Q
from .permissions import IsNeedyOrReadOnly


class NeedViewSet(viewsets.ModelViewSet):
    queryset = Need.objects.all()
    serializer_class = NeedSerializer
    lookup_field = 'slug'
    permission_classes = [IsNeedyOrReadOnly]

    def get_queryset(self):
        queryset = Need.objects.all()
        q = self.request.query_params.get('q')
        date_filter = self.request.query_params.get('date')
        kind_filter = self.request.query_params.get('kind')

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(address__icontains=q)
            )

        if date_filter:
            today = now().date()
            if date_filter == 'today':
                queryset = queryset.filter(created__date=today)
            elif date_filter == '2days':
                queryset = queryset.filter(created__date__gte=today - timedelta(days=2))
            elif date_filter == 'week':
                queryset = queryset.filter(created__date__gte=today - timedelta(days=7))

        if kind_filter:
            queryset = queryset.filter(kind__slug__icontains=kind_filter)

        return queryset