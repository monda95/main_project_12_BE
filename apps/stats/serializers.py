from rest_framework import serializers


class PopularQuerySerializer(serializers.Serializer):
    query = serializers.CharField()
    count = serializers.IntegerField()


class DailySignupSerializer(serializers.Serializer):
    date = serializers.DateField()
    count = serializers.IntegerField()


class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    daily_signups_last_7_days = DailySignupSerializer(many=True)
