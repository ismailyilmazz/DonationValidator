from appuser.models import Role,AppUser

def user_permissions(request):
    if request.user.is_authenticated:
        try:
            role = AppUser.objects.get(user=request.user).all_values()["role"] 
            return {"user_permissions": role.permissions}
        except:
            return {"user_permissions": []}
    return {"user_permissions": []}
