from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles):
    """
    Decorator for views that checks whether a user has a specific role.
    allowed_roles should be a list of strings, e.g., ['PROPRIETOR', 'DOCTOR']
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
                
            raise PermissionDenied("You do not have the required role to access this page.")
        return _wrapped_view
    return decorator
