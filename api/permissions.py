from rest_framework import permissions

class IsNeedyOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Erişim izinleri
        return obj.needy == request.user