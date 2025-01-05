from rest_framework import generics, status
from rest_framework.response import Response
import logging
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render
from .models import Event, Currency, User
from .serializers import EventSerializer, CurrencySerializer, UserSerializer
from twilio.rest import Client
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)
# Create your views here.

class EventList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get(self, request, *args, **kwargs):
        logger.debug("Received GET request")
        return super().get(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        event_id = kwargs.get('pk')
        try:
            event = Event.objects.get(pk=event_id)
            event.type = request.data.get('type')
            event.currency = request.data.get('currency')
            event.amount = request.data.get('amount')
            event.rate = request.data.get('rate')
            event.total = request.data.get('total')
            event.save()
            return Response(status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            logger.error(f"Event with ID {event_id} not found")
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating event: {str(e)}")
            return Response(
                {"error": "Failed to update event"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, *args, **kwargs):
        logger.debug(f"Received POST data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Validation errors: {serializer.errors}")
        return Response(
            {
                "error": "Invalid data",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, *args, **kwargs):
        event_id = kwargs.get('pk')
        logger.debug(f"Attempting to delete event with ID: {event_id}")

        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            logger.error(f"Event with ID {event_id} not found")
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting event: {str(e)}")
            return Response(
                {"error": "Failed to delete event"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CurrencyList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.method == 'GET':
            return Currency.objects.values('name')
        return Currency.objects.all()
    serializer_class = CurrencySerializer

    def delete(self, request, *args, **kwargs):
        currency_name = request.data.get('name')
        try:
            currency = Currency.objects.get(name=currency_name)
            currency.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Currency.DoesNotExist:
            logger.error(f"Currency with name {currency_name} not found")
            return Response(
            {"error": "Currency not found"},
            status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting currency: {str(e)}")
            return Response(
            {"error": "Failed to delete currency"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, *args, **kwargs):
        currency_name = request.data.get('newName')
        currency_old_name = request.data.get('oldName')
        try:
            currency = Currency.objects.get(name=currency_old_name)
            currency.name = currency_name
            currency.save()
            return Response(status=status.HTTP_200_OK)
        except Currency.DoesNotExist:
            logger.error(f"Currency with name {currency_old_name} not found")
            return Response(
                {"error": "Currency not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating currency: {str(e)}")
            return Response(
                {"error": "Failed to update currency"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class UsersList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        if not kwargs.get('username'):
            return super().get(request, *args, **kwargs)
        user_id = kwargs.get('username')
        return Response(
            UserSerializer(User.objects.get(username=user_id)).data,
            status=status.HTTP_200_OK
        )

    def post(self, request, *args, **kwargs):
        logger.debug(f"Received POST data: {request.data}")
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {
                    "error": "Имя пользователя уже занято",
                    "details": "A user with this username already exists"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif User.objects.filter(email=request.data.get('email')).exists():
            return Response(
                {
                    "error": "Эта почта уже зарегистрирована",
                    "details": "A user with this email already exists"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif User.objects.filter(phone=request.data.get('phone')).exists():
            return Response(
                {
                    "error": "Этот номер уже зарегистрирован",
                    "details": "A user with this phone number already exists"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
            
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Get validated data
            validated_data = serializer.validated_data
            # Remove password from validated data
            password = validated_data.pop('password', None)
            # Create user instance
            user = User(**validated_data)
            # Set password properly to ensure it's hashed
            user.set_password(password)
            user.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        logger.error(f"Validation errors: {serializer.errors}")
        return Response(
            {
                "error": "Invalid data",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, *args, **kwargs):
        new_user_id = request.data.get('username')
        old_user_id = request.data.get('oldUsername')
        is_superuser = request.data.get('isSuperUser')
        email = request.data.get('email')
        logger.debug(is_superuser)
        print(is_superuser)
        if request.data.get('password'):
            new_password = request.data.get('password')
        else:
            new_password = None
        try:
            user = User.objects.get(username=old_user_id)
            if new_password:
                user.set_password(new_password)
            user.username = new_user_id
            user.is_superuser = True if is_superuser else False
            user.email = email
            user.save()
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"User with ID {old_user_id} not found")
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return Response(
                {"error": "Failed to update user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        user_id = request.data.get('username')
        logger.debug(f"Attempting to delete user with ID: {user_id}")
        try:
            user = User.objects.get(username=user_id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} not found")
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return Response(
                {"error": "Failed to delete user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserAuthentication(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                # Generate token
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Authentication successful",
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetRequest(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        if email.startswith("+") or "@" not in email:
            try:
                sid = settings.TWILIO_ACCOUNT_SID
                token = settings.TWILIO_AUTH_TOKEN
                client = Client(sid, token)
                user = User.objects.get(phone=email)
                print(user.phone)
                # Use custom token generation instead of default_token_generator
                token = self.generate_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}"
                print(reset_url)
                

            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            except (Exception) as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            messages = client.messages.create(
                    body="Ваша ссылка для сброса пароля: " + reset_url,
                    from_= "+17077350736",
                    to=user.phone
                )
            print(messages.sid, messages.status, messages.body)
            return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)

        else:
            try:
                user = User.objects.get(email=email)
                token = self.generate_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}"
                send_mail(
                    'Запрос на сброс пароля',
                    f'<h1>Сброс пароля</h1><br>Для сброса пароля перейдите по ссылке: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                    html_message=f'<html><body style="text-align: center; background: linear-gradient(158deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1) 60%, rgba(0,226,255,1) 100%); padding: 100px 0;"><h1 style="color:#3EA1F2; font-size: 32px">Сброс пароля.</h1><h3 style="color: white; font-size: 20px">Был запрошен сброс пароля для пользователя {user.username},<br><span style="color: #FF4545">если это были не вы, не реагируйте на это письмо.</span><br>Для сброса пароля нажмите кнопку ниже.</h3><a href="{reset_url}" style="color: #ffffff; text-decoration: none;"><button style="padding: 15px 50px; color: #ffffff; background: linear-gradient(90deg, #42A4F5, #2088E5); border-radius:10px; border: none">Cброс пароля</button></a></body></html>'
                )
                return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def generate_token(self, user):
        from hashlib import sha256
        from django.utils import timezone
        # Token valid for 24 hours
        timestamp = int(timezone.now().timestamp())
        # Round timestamp to hours to give 1-hour validity window
        timestamp_hours = timestamp - (timestamp % 3600)
        token_string = f"{user.email}-{user.id}-{user.password}-{timestamp_hours}"
        return sha256(token_string.encode()).hexdigest()[:32]

class PasswordResetConfirm(APIView):
    permission_classes = [AllowAny]
    template_name = 'password_reset_confirm.html'

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            # Verify token and check expiration
            if self.check_token(user, token):
                return render(request, self.template_name, {
                    'validlink': True,
                    'uidb64': uidb64,
                    'token': token
                })
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            pass
        return render(request, self.template_name, {'validlink': False})

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if self.check_token(user, token):
                password1 = request.POST.get('new_password1')
                password2 = request.POST.get('new_password2')

                if not password1 or not password2:
                    return render(request, self.template_name, {
                        'validlink': True,
                        'error': 'Please enter both passwords',
                        'token': token,
                        'uidb64': uidb64
                    })

                if password1 != password2:
                    return render(request, self.template_name, {
                        'validlink': True,
                        'error': 'Passwords do not match',
                        'token': token,
                        'uidb64': uidb64
                    })

                if len(password1) < 8:
                    return render(request, self.template_name, {
                        'validlink': True,
                        'error': 'Пароль должен содержать не менее 8 символов',
                        'token': token,
                        'uidb64': uidb64
                    })

                user.set_password(password1)
                user.save()
                return render(request, self.template_name, {
                    'validlink': True,
                    'success': True
                })

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            pass

        return render(request, self.template_name, {'validlink': False})

    def check_token(self, user, token):
        # Recreate token and verify it matches
        from hashlib import sha256
        from django.utils import timezone
        try:
            current_time = int(timezone.now().timestamp())
            # Check last 24 hours in 1-hour intervals
            for hours in range(24):
                check_time = current_time - (current_time % 3600) - (hours * 3600)
                token_string = f"{user.email}-{user.id}-{user.password}-{check_time}"
                expected_token = sha256(token_string.encode()).hexdigest()[:32]
                if token == expected_token:
                    return True
            return False
        except Exception:
            return False

class ClearAll(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        superAdminsList = User.objects.filter(is_superuser=True)
        for superAdmin in superAdminsList: 
            if superAdmin.username == username and check_password(password, superAdmin.password):
                Event.objects.all().delete()
                return Response({"message": "Clear successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class isSuperAdmin(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        username = kwargs.get('username')
        try:
            superAdmin = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Not superadmin"}, status=status.HTTP_400_BAD_REQUEST)
        if superAdmin.is_superuser:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Not superadmin"}, status=status.HTTP_400_BAD_REQUEST)
    
class testRenderResetTemplateUi(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        return render(request, 'password_reset_confirm.html', {'validlink': True, 'uidb64': 'uidb64', 'token': 'token'})