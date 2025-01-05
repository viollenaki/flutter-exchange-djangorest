from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
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

class CustomTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                refresh = RefreshToken()
                
                # Add custom claims
                refresh['user_id'] = user.id
                refresh['username'] = user.username
                refresh['email'] = user.email
                refresh['is_superuser'] = user.is_superuser

                return {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            else:
                raise serializers.ValidationError('Неверный пароль')
        except User.DoesNotExist:
            print('Пользователь не найден')
            raise serializers.ValidationError('Пользователь не найден')