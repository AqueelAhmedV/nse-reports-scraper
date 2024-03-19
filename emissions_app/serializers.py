from rest_framework import serializers
from .models import EmissionReport

class EmissionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionReport
        fields = '__all__'