from django.contrib import admin
from .models import CustomUser, Waitlist

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
	list_display = ('email', 'first_name', 'last_name', 'wallet_address', 'public_key', 'is_staff', 'is_active')
	search_fields = ('email', 'first_name', 'last_name', 'wallet_address')
	readonly_fields = ('wallet_address', 'public_key', 'encrypted_private_key')


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
	list_display = ('email', 'first_name', 'last_name', 'created_at')
	search_fields = ('email', 'first_name', 'last_name')
	readonly_fields = ('created_at',)
