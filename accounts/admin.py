from django.contrib import admin
from .models import UserAccount


class AccountsAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'lastname', 'username', 'phone', 'email', 'country')
    list_display_links = ('id', 'firstname', 'lastname')
    # list_filter = ('firstname', 'lastname')
    search_fields = ('firstname', 'lastname')


admin.site.register(UserAccount, AccountsAdmin)