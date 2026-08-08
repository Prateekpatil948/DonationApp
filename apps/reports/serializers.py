"""Response serializers for the reports app (documentation only - views return plain dicts)."""

from rest_framework import serializers


class ReportFilterQuerySerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    category = serializers.UUIDField(required=False)
    member = serializers.UUIDField(required=False)
    payment_mode = serializers.ChoiceField(choices=["CASH", "UPI"], required=False)
    export = serializers.ChoiceField(choices=["csv", "excel", "pdf"], required=False)


class SummaryReportResponseSerializer(serializers.Serializer):
    total_collection = serializers.DecimalField(max_digits=12, decimal_places=2)
    donation_count = serializers.IntegerField()
    cash_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    upi_total = serializers.DecimalField(max_digits=12, decimal_places=2)


class CategoryReportRowSerializer(serializers.Serializer):
    category_id = serializers.UUIDField()
    category_name = serializers.CharField()
    goal_amount = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    collected_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    donation_count = serializers.IntegerField()
    progress_percent = serializers.FloatField(allow_null=True)


class MemberReportRowSerializer(serializers.Serializer):
    member_id = serializers.UUIDField()
    member_name = serializers.CharField()
    phone_number = serializers.CharField()
    total_collected = serializers.DecimalField(max_digits=12, decimal_places=2)
    donation_count = serializers.IntegerField()


class DateReportRowSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_collected = serializers.DecimalField(max_digits=12, decimal_places=2)
    donation_count = serializers.IntegerField()
    cash_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    upi_total = serializers.DecimalField(max_digits=12, decimal_places=2)
