from rest_framework import serializers
from .models import Event, Currency

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('total',)

    def validate(self, data):
        data['total'] = data['amount'] * data['rate']
        return data

    def create(self, validated_data):
        return Event.objects.create(**validated_data)

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'