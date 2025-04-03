from django.contrib.auth.models import User
from django.views.generic import DetailView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest

from feed.models import Post
from followers.models import Follower

from .forms import ProfileForm
from .models import Profile


class ProfileDetailView(DetailView):
    http_method_names = ["get"]
    template_name = "profiles/detail.html"
    model = User
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.get_object()
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.filter(author=user).count()
        # context['total_followers'] = ...
        if self.request.user.is_authenticated:
            context['total_followers'] = Follower.objects.filter(following=self.request.user).count()
            context['you_follow'] = Follower.objects.filter(following=user, followed_by=self.request.user).exists()
        return context


class FollowView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()

        if "action" not in data or "username" not in data:
            return HttpResponseBadRequest("Missing data")

        try:
            other_user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return HttpResponseBadRequest("Missing user")

        if data['action'] == "follow":
            # Follow
            follower, created = Follower.objects.get_or_create(
                followed_by=request.user,
                following=other_user
            )
        else:
            # Unfollow
            try:
                follower = Follower.objects.get(
                    followed_by=request.user,
                    following=other_user,
                )
            except Follower.DoesNotExist:
                follower = None

            if follower:
                follower.delete()

        return JsonResponse({
            'success': True,
            'wording': "Unfollow" if data['action'] == "follow" else "Follow"
        })
    
class ModifyProfile(FormView):
    template_name = 'profiles/modify.html'
    form_class = ProfileForm 
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        owner = User.objects.get (id=self.request.user.id)
        owner.username = form.cleaned_data['username']
        owner.save()  

        owner = Profile.objects.get (id=self.request.user.id)
        owner.image = form.cleaned_data['avatar']
        owner.save()  
        return super().form_valid(form)