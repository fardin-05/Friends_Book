from django.urls import path
from .views import (
    HomeView,
    RegisterView,
    CustomLoginView,
    CustomLogoutView,
    ProfileView,
    EditProfileView,
    PostUpdateView,
    PostDeleteView,
    AdminDashboardView,
    AdminPostListView,
    AdminUserListView,
)
from . import views

urlpatterns = [

    # 🏠 HOME
    path('', HomeView.as_view(), name='home'),

    # 🔐 AUTH
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    # 👤 PROFILE
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', EditProfileView.as_view(), name='edit_profile'),

    # 📝 POST
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='edit_post'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='delete_post'),

    # 🔥 SOCIAL ACTIONS
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('react/<int:post_id>/<str:reaction_type>/', views.react_post, name='react_post'),

    # 🛠️ ADMIN PANEL
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    path('dashboard/users/', AdminUserListView.as_view(), name='admin_users'),
    path('dashboard/posts/', AdminPostListView.as_view(), name='admin_posts'),

    #inbox & chat 
    path('inbox/', views.inbox, name='inbox'),
    path("chat/<int:user_id>/", views.chat_view, name="chat"),
    path('inbox/check/', views.check_inbox, name='check_inbox'),

    #notification
    path('notifications/', views.notifications, name='notifications'),


    #file send
    path('chat/upload/<int:conversation_id>/', views.upload_chat_file, name='upload_chat_file'),

    #message seen unseen
    path('chat/seen/<int:conversation_id>/', views.mark_seen, name='mark_seen'),

    #user search
    path('search/', views.search_users, name='search'),
]