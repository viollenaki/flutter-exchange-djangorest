from rest_framework import serializers
from .models import Event, Currency, User

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
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }