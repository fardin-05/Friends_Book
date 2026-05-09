from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView

from .models import Post, Profile, UserModel, Comment, Like, Notification, Conversation, Message
from .forms import CustomUserCreationForm, PostForm, ProfileEditForm
from django.http import JsonResponse
from .utils import get_or_create_conversation

#=====Admin Section===========

from django.http import HttpResponseForbidden
# 🔐 common admin check mixin
class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class AdminDashboardView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        # ❌ login নাই → login page
        if not request.user.is_authenticated:
            return redirect('login')

        # ❌ superuser না → block
        if not request.user.is_superuser:
            return HttpResponseForbidden("🚫 You are not admin!")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        users = UserModel.objects.all()
        posts = Post.objects.all().order_by('-created_at')

        return render(request, 'api/dashboard.html', {
            'users': users,
            'posts': posts,
        })

# 👤 User List
class AdminUserListView(AdminRequiredMixin, View):
    def get(self, request):
        users = UserModel.objects.all()
        return render(request, 'api/admin_users.html', {'users': users})

# 📝 Post List
class AdminPostListView(AdminRequiredMixin, View):
    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        return render(request, 'api/admin_posts.html', {'posts': posts})



# 🏠 HomeView

@method_decorator(login_required, name='dispatch')
class HomeView(View):

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-created_at')

        # 🔥 user reaction dictionary
        user_reactions = {}

        likes = Like.objects.filter(user=request.user)

        for like in likes:
            user_reactions[like.post.id] = like.reaction_type

        context = {
            'posts': posts,
            'user_reactions': user_reactions
        }

        return render(request, 'api/home.html', context)


    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            return redirect('home')

        posts = Post.objects.all().order_by('-created_at')

        # 🔥 AGAIN add reactions (important)
        user_reactions = {}

        likes = Like.objects.filter(user=request.user)

        for like in likes:
            user_reactions[like.post.id] = like.reaction_type

        context = {
            'posts': posts,
            'form': form,
            'user_reactions': user_reactions
        }

        return render(request, 'api/home.html', context)


# 🧍‍♂️ RegisterView
class RegisterView(CreateView):
    model = UserModel
    form_class = CustomUserCreationForm
    template_name = 'api/register.html'
    success_url = reverse_lazy('login')


# 🔐 Custom Login & Logout
class CustomLoginView(LoginView):
    template_name = 'api/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


# 👤 Profile View
class ProfileView(DetailView):
    model = UserModel
    template_name = 'api/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return get_object_or_404(UserModel, email=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_obj = context['profile_user']

        profile, created = Profile.objects.get_or_create(user=user_obj)

        context['profile'] = profile
        context['posts'] = Post.objects.filter(user=user_obj)

        return context


# ✏️ Edit Profile View
class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileEditForm
    template_name = 'api/edit_profile.html'

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.request.user.email})



# ✏️ Edit Post
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'api/edit_post.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user or self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy('home')


# ❌ Delete Post
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'api/delete_post.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user or self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy('home')


@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')

        if content:
            # 💬 comment create
            Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )

            # 🔔 notification create
            if post.user != request.user:
                Notification.objects.create(
                    user=post.user,
                    message=f"{request.user.full_name} commented on your post"
                )

    return redirect('home')


@login_required

def react_post(request, post_id, reaction_type):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    reaction = Like.objects.filter(post=post, user=user).first()

    current_reaction = None

    if reaction:
        if reaction.reaction_type == reaction_type:
            reaction.delete()
            current_reaction = None
        else:
            reaction.reaction_type = reaction_type
            reaction.save()
            current_reaction = reaction_type
    else:
        Like.objects.create(
            post=post,
            user=user,
            reaction_type=reaction_type
        )
        current_reaction = reaction_type

    return JsonResponse({
        "reaction": current_reaction,
        "count": post.likes.count()
    })




#=====chat system logic========

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(participants=request.user)

    convo_data = []

    for convo in conversations:
        other_user = convo.get_other_user(request.user)

        # ✅ other_user None হলে skip করো
        if not other_user:
            continue

        # ✅ other_user এর id নেই হলেও skip
        if not other_user.id:
            continue

        last_msg = convo.messages.order_by('-created_at').first()

        convo_data.append({
            "id": convo.id,
            "other_user": other_user,
            "last_msg": last_msg,
            "has_unread": convo.messages.filter(is_seen=False).exclude(sender=request.user).exists(),
            "unread_count": convo.messages.filter(is_seen=False).exclude(sender=request.user).count()
        })

    return render(request, 'api/inbox.html', {
        'conversations': convo_data
    })

@login_required
def check_inbox(request):

    has_new = Message.objects.filter(
        conversation__participants=request.user,
        is_seen=False
    ).exclude(sender=request.user).exists()

    return JsonResponse({
        "new_message": has_new
    })


@login_required
def chat_view(request, user_id):
    other_user = get_object_or_404(UserModel, id=user_id)

    convo = get_or_create_conversation(request.user, other_user)

    if request.method == "POST":
        content = request.POST.get("content", "")
        file = request.FILES.get("file")

        file_type = None
        if file:
            name = file.name.lower()
            if name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                file_type = 'image'
            elif name.endswith(('.mp4', '.webm', '.mov')):
                file_type = 'video'
            elif name.endswith('.pdf'):
                file_type = 'pdf'
            elif name.endswith(('.doc', '.docx')):
                file_type = 'docx'
            else:
                file_type = 'file'

        if content or file:
            Message.objects.create(
                conversation=convo,
                sender=request.user,
                content=content,
                file=file,
                file_type=file_type
            )

        return redirect('chat', user_id=user_id)

    messages = convo.messages.all()

    return render(request, "api/chat.html", {
        "messages": messages,
        "conversation": convo,
        "other_user": other_user
    })

@login_required
def upload_chat_file(request, conversation_id):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            return JsonResponse({"error": "No file"}, status=400)

        name = file.name.lower()
        if name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            file_type = 'image'
        elif name.endswith(('.mp4', '.webm', '.mov')):
            file_type = 'video'
        elif name.endswith('.pdf'):
            file_type = 'pdf'
        elif name.endswith(('.doc', '.docx')):
            file_type = 'docx'
        else:
            file_type = 'file'

        convo = get_object_or_404(Conversation, id=conversation_id)
        msg = Message.objects.create(
            conversation=convo,
            sender=request.user,
            file=file,
            file_type=file_type
        )

        return JsonResponse({
            "file_url": msg.file.url,
            "file_type": file_type,
            "file_name": file.name,
        })

    return JsonResponse({"error": "Invalid method"}, status=405)


@login_required
def mark_seen(request, conversation_id):
    if request.method == "POST":
        convo = get_object_or_404(Conversation, id=conversation_id)
        # আমার কাছে আসা unseen message গুলো seen করো
        Message.objects.filter(
            conversation=convo,
            is_seen=False
        ).exclude(sender=request.user).update(is_seen=True)

        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Invalid method"}, status=405)





#=====notification========
@login_required
def notifications(request):
    notifs = request.user.notifications.all().order_by('-created_at')

    return render(request, 'api/notifications.html', {
        'notifications': notifs
    })




#=======User Search=========
@login_required
def search_users(request):
    query = request.GET.get('q', '')
    fmt = request.GET.get('format', '')
    results = []

    if query:
        qs = UserModel.objects.filter(
            full_name__icontains=query
        ).exclude(id=request.user.id) | UserModel.objects.filter(
            email__icontains=query
        ).exclude(id=request.user.id)

        if fmt == 'json':
            data = []
            for u in qs:
                try:
                    avatar = u.profile.profile_picture.url
                except:
                    avatar = f"https://ui-avatars.com/api/?name={u.full_name}&background=7f00ff&color=fff"
                data.append({
                    'full_name': u.full_name,
                    'email': u.email,
                    'avatar': avatar,
                })
            return JsonResponse({'results': data})

        results = qs

    return render(request, 'api/search.html', {
        'results': results,
        'query': query
    })