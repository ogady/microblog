from django.contrib import admin
from blog.models import Blog, Comment
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import ugettext_lazy
# Register your models here.

admin.site.register(Blog)
admin.site.register(Comment)


# adminサイトでemailを使う
class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (ugettext_lazy('Personal info'), {'fields': ('nick_name',)}),
        (ugettext_lazy('Permissions'), {'fields': ('is_active', 'is_staff',
                                                   'is_superuser', 'groups', 'user_permissions')}),
        (ugettext_lazy('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'nick_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'nick_name')
    ordering = ('email',)


admin.site.register(User, MyUserAdmin)