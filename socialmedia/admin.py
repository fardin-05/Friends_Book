from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserModel, Profile, Post, Comment, Like
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


# ✅ Custom User Forms
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ('email', 'full_name')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = UserModel
        fields = '__all__'


# ✅ User Admin
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ['id', 'email', 'full_name', 'role', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'role']
    search_fields = ['email', 'full_name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2')}
        ),
    )


admin.site.register(UserModel, CustomUserAdmin)


# ✅ Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']
    search_fields = ['user__email']


# ✅ Post Admin (🔥 important)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'content', 'created_at']
    search_fields = ['content', 'user__email']
    list_filter = ['created_at']
    ordering = ['-created_at']


# ✅ Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'created_at']
    search_fields = ['user__email', 'post__content']
    list_filter = ['created_at']


# ✅ Like Admin
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post']
    search_fields = ['user__email']


from .models import Conversation, Message

admin.site.register(Conversation)
admin.site.register(Message)