from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import EmissionReport
from .serializers import EmissionReportSerializer

class EmissionReportViewSet(viewsets.ModelViewSet):
    queryset = EmissionReport.objects.all()
    serializer_class = EmissionReportSerializer