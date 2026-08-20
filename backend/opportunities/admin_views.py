from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import IsAdminUser
from .models import AccountProfile


User = get_user_model()


class AdminAccountView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    class RoleSerializer(serializers.Serializer):
        role = serializers.ChoiceField(choices=AccountProfile.ROLE_CHOICES)

    @staticmethod
    def row(profile):
        return {
            "id": profile.id,
            "public_id": str(profile.public_id),
            "name": profile.user.get_full_name() or profile.user.username,
            "email": profile.user.email,
            "role": profile.role,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }

    def get(self, request):
        profiles = AccountProfile.objects.select_related("user").all()
        return Response({"accounts": [self.row(profile) for profile in profiles]})

    def patch(self, request, account_id):
        profile = get_object_or_404(AccountProfile.objects.select_related("user"), id=account_id)
        payload = self.RoleSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        if profile.user_id == request.user.id and payload.validated_data["role"] != "admin":
            return Response({"detail": "You cannot remove your own administrator role."}, status=status.HTTP_400_BAD_REQUEST)
        profile.role = payload.validated_data["role"]
        profile.save(update_fields=["role", "updated_at"])
        return Response(self.row(profile))
