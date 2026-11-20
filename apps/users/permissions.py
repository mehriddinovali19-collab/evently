from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
     """Faqat role='admin' bo'lgan foydalanuvchilar uchun"""
     def has_permission(self, request, view):
          return bool(request.user and request.user.is_authenticated and request.user.role == 'admin' or request.user.is_staff)


class IsAdminOrReadonly(permissions.BasePermission):
     """Get/HEAD/OPTIONS hammaga, O'zgartirish faqat adminga"""
     def has_permission(self, request, view):
          if request.method in permissions.SAFE_METHODS:
               return True 
          return bool(request.user and request.user.is_authenticated and request.user.role == 'admin' or request.user.is_staff)
     

     