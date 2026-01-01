from rest_framework import serializers
from .models import Contact, Reviewer

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'postcode', 'name', 'phone', 'address', 'email', 'notes', 'label', 'created_at']
        read_only_fields = ['id', 'created_at']

class ReviewerSerializer(serializers.ModelSerializer):
    """责编信息序列化器"""
    class Meta:
        model = Reviewer
        fields = [
            'id', 'year', 'period', 'name', 'workplace',
            'id_card', 'bank_account', 'bank_name', 'phone',
            'gross_pay', 'tax', 'net_pay', 'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at'] 