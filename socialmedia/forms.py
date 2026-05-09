# forms.py

from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, UserModel

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']

class PostForm(forms.ModelForm):
    # ফর্মের লেবেল পরিবর্তন করতে চাইলে widget ব্যবহার করতে পারো
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'write somthing about your feelings...'}),
        required=False
    )
    
    class Meta:
        model = Post
        # user এবং created_at ফিল্ডগুলো ফর্ম থেকে বাদ দিলাম, কারণ এগুলো View-তে সেট করা হবে
        fields = ['content', 'image']

class CustomUserCreationForm(UserCreationForm):
    # এই ফিল্ডগুলো ইউজারের কাছ থেকে ইনপুট নিতে হবে
    full_name = forms.CharField(max_length=200, label='Full Name')
    email = forms.EmailField(label='e-mail (valid email required for login)')

    class Meta:
        model = UserModel
        # পাসওয়ার্ড, ইমেইল এবং পুরো নাম চাইবে
        fields = ('email', 'full_name')
        
    def save(self, commit=True):
        # UserManager-এর create_user ফাংশন ব্যবহার করে ইউজার তৈরি করবে
        user = UserModel.objects.create_user(
            email=self.cleaned_data["email"],
            full_name=self.cleaned_data["full_name"],
            password=self.cleaned_data["password2"], # পাসওয়ার্ড পাস করা হলো
            is_active=True # রেজিস্ট্রেশনের পর সক্রিয় করা হলো
        )
        return user


