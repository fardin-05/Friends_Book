from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
# Custom User Manager
class UserManager (BaseUserManager):
    def create_user(self, email, full_name, password = None, **extra_fields):
        if not email:
            raise ValueError("Email Field is Must be Required")
        email = self.normalize_email(email)
        user = self.model(email = email, full_name = full_name, **extra_fields )
        user.set_password(password)
        user.save(using = self._db)
        return user
    def create_superuser(self, email, full_name, password = None, **extra_fields ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('role', 'admin')
        if extra_fields.get('is_staff') is not True:
            raise ValueError("SuperUser Must Have is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser Must Have is_superuser=True")
        return self.create_user(email, full_name, password, **extra_fields)
    


#Custom User Model
class UserModel(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique = True)
    full_name = models.CharField(max_length = 200)
    role = models.CharField(max_length = 20, choices = ROLE_CHOICES, default = 'user')
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default = True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups', # <--- নতুন unique নাম
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        verbose_name=('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions', # <--- নতুন unique নাম
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name=('user permissions'),
    )
    

    def __str__(self):
        return f"{self.email} ({self.role})"
class Profile(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)

    profile_picture = models.ImageField(
        upload_to='profiles/',
        default='profiles/default.jpg'
    )
    
    def __str__(self):
        return f"{self.user.full_name}'s Profile"

class Post(models.Model):
    # কোন ইউজার পোস্ট করেছে
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True) # টেক্সট কন্টেন্ট
    image = models.ImageField(upload_to='posts/', blank=True, null=True) # ছবি আপলোড
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # সাম্প্রতিক পোস্টগুলো আগে দেখাবে
        ordering = ['-created_at'] 

    def __str__(self):
        return f"Post by {self.user.full_name} on {self.created_at.strftime('%Y-%m-%d')}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.full_name} on Post {self.post.id}"

class Like(models.Model):
    REACTION_CHOICES = (
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('care', 'Care'),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES, default='like')

    class Meta:
        unique_together = ('post', 'user')

    

#======chat system=======

class Conversation(models.Model):
    participants = models.ManyToManyField(UserModel)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"
    
    def get_other_user(self, user):
        return self.participants.exclude(id=user.id).first()
    
    


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    file_type = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.full_name}: {self.content[:20]}"


#====notification======
class Notification(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message