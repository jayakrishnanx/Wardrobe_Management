from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, RegularUser, Supplier


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

@admin.register(RegularUser)
class RegularUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_active', 'last_login', 'date_joined')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('username', 'email')
    
    # Only show 'user' role
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='user')

    # Default new users to 'user' role
    def save_model(self, request, obj, form, change):
        if not change:
            obj.role = 'user'
        super().save_model(request, obj, form, change)

@admin.register(Supplier)
class SupplierAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_active', 'last_login', 'date_joined')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('username', 'email')

    # Only show 'supplier' role
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='supplier')

    # Default new users to 'supplier' role
    def save_model(self, request, obj, form, change):
        if not change:
            obj.role = 'supplier'
        super().save_model(request, obj, form, change)
