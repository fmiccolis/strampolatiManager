from rest_framework import serializers

from api.models import Event, Location, Type, Contact, Provider, User


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('province', 'city', 'name', 'latitude', 'longitude')


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ('name',)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('full_name', 'additional_info', 'phone')


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ("first_name", "last_name")


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class EventSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    contact = ContactSerializer(read_only=True)
    provider = ProviderSerializer(read_only=True)
    agents = AgentSerializer(read_only=True, many=True)

    class Meta:
        model = Event
        fields = (
            'start_date', 'end_date', 'distance', 'location',
            'type', 'contact', 'provider', 'agents', 'payment',
            'extra'
        )
