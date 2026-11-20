from rest_framework import permissions


class IsAdmin(permissions.BasePermission):                                                                                                                    
        """                                                                                                                                                       
        Faqat roli 'admin' bo'lgan yoki is_staff=True bo'lgan foydalanuvchilar uchun.                                                                             
        """                                                                                                                                                       
        def has_permission(self, request, view):                                                                                                                  
            return bool(                                                                                                                                          
                request.user and                                                                                                                                  
                request.user.is_authenticated and                                                                                                                 
                (getattr(request.user, 'role', None) == 'admin' or request.user.is_staff)                                                                         
            ) 


class IsAdminOrReadonly(permissions.BasePermission):                                                                                                          
        """                                                                                                                                                       
        GET, HEAD, OPTIONS (o'qish) so'rovlari barchaga ochiq.                                                                                                    
        POST, PUT, PATCH, DELETE (yaratish/o'zgartirish) faqat adminlar yoki staff uchun.                                                                         
        """                                                                                                                                                       
        def has_permission(self, request, view):                                                                                                                  
            if request.method in permissions.SAFE_METHODS:                                                                                                        
                return True
  
            return bool(
                request.user and 
                request.user.is_authenticated and 
                (getattr(request.user, 'role', None) == 'admin' or request.user.is_staff)
            )
     