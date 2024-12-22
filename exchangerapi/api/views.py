from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

from .models import *
from .serializers import *
# Create your views here.

class EventList(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

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

class CurrencyList(generics.ListCreateAPIView):
    # get only currency name for GET requests
    def get_queryset(self):
        if self.request.method == 'GET':
            return Currency.objects.values('name')
        return Currency.objects.all()
    serializer_class = CurrencySerializer

