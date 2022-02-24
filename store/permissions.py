from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS, \
    DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # if request.method == "GET":
        if request.method in SAFE_METHODS:   # this is better approach
            return True
        return bool(request.user and request.user.is_staff)


class MyFullDjangoModelPermissions(DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map["GET"] = ['%(app_label)s.view_%(model_name)s']


class ViewCustomerHistoryPermission(BasePermission):
    def has_permission(self, request, view):
                                    # app_name.permission   # defined in models
        return request.user.has_perm('store.view_history')