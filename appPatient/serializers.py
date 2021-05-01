from rest_framework import serializers
from .models import Visit


class VisitRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.BooleanField()
    doctor_id = serializers.IntegerField()
    datetime = serializers.DateTimeField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class VisitSerializer(serializers.ModelSerializer):
    def create(self, validated_date):
        visit = Visit.objects.create(
            id=validated_date['id'],
            status=validated_date['status'],
            datetime=validated_date['datetime'],
            doctor_id=validated_date['doctor_id'],
            patient_id=validated_date['patient_id']
        )
        visit.save()
        return visit

    class Meta:
        model = Visit
        fields = ['id', 'id', 'status', 'datetime', 'doctor_id', 'patient_id']
