from rest_framework import serializers
from app.models import User, RefUser



class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(read_only=True)
    invite_code = serializers.CharField(read_only=True)
    referrals_given = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['phone', 'referrals_given', "invite_code"]

    def get_referrals_given(self, obj):
        referrals = obj.referrals_given.all()
        return [ref_user.who_user_id.phone for ref_user in referrals]




class RefUserSerializer(serializers.ModelSerializer):
    user_id = UserSerializer(read_only=True)
    who_user_id = UserSerializer(read_only=True)
    class Meta:
        model = RefUser
        fields = '__all__'