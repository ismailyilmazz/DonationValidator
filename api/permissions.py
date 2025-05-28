from rest_framework import permissions

class IsNeedyOrReadOnly(permissions.BasePermission):
    """
    Sadece ilgili 'Need' kaydının sahibi (needy) PUT, PATCH ve DELETE yapabilir.
    Diğer herkes sadece GET yapabilir.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Erişim izinleri
        return obj.needy == request.user