from rest_framework import serializers
from django.utils import timezone
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Event 
        fields = [
            'id', 'title',
            'description',
            'event_type',
            'location',
            'start_at',
            'end_at',
            'capacity',
            'status',
            'created_at',
            'updated_at',
            'created_by'
        ]
        read_only_fields = [
            'id',
            'status',
            'created_by', 
            'created_at',
            'updated_at',
        ]


    def validate(self, attrs):
        start_at = attrs.get('start_at', getattr(self.instance, 'start_at', None))
        end_at = attrs.get('end_at', getattr(self.instance, 'end_at', None))


        # end_at har doim start_at dan katta bulish kerak 
        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({"end_at": "Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak."})

        #yangi yartilyotgan event o'tib ketgan sanada bo'lmasilig kerka buladi
        if not self.instance and start_at and start_at <= timezone.now():
            raise serializers.ValidationError({"start_at": "Tadbir boshlanish vaqti kelajakda bo'lishi kerak."})

        return attrs




    def validate_capacity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Capacity 0 dan katta bo'lish shart!")
        return value 