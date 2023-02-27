from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import Profile
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .utills import searchProfiles, paginateProfiles

# Create your views here.
# ---------------------Login & Register -----------------------------
class UserLoginView(View):
    page = 'login'
    template_name = 'users/login-register.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profiles')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        context = {'page': self.page}
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')


        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request, 'Username OR password is incorrect')

        context = {'page': self.page}
        return render(request, self.template_name, context)


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.info(request, 'User was logged out!')
        return redirect('profiles')


class UserRegistrationView(View):
    page = 'register'
    template_name = 'users/login-register.html'
    form_class = CustomUserCreationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profiles')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {
            'page': self.page,
            'form': form,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created!')

            login(request, user)
            return redirect('edit-account')
        else:
            context = {
                'page': self.page,
                'form': form,
            }
            return render(request, self.template_name, context)


# --------------------Profile Read ------------------------------------
class ProfilesView(View):
    template_name = 'users/profiles.html'

    def get(self, request):
        profiles, search_query = searchProfiles(request)
    
        custom_range, profiles = paginateProfiles(request, profiles, 3)

        context = {
            'profiles': profiles,
            'search_query': search_query,
            'custom_range': custom_range,
        }
        return render(request, self.template_name, context)


class ProfileDetailView(View):
    template_name = 'users/user-profile.html'
    def dispatch(self, request, *args, **kwargs):
        self.profileObj = Profile.objects.get(id=kwargs['pk'])
        
        if request.user.profile == self.profileObj:
            return redirect('account')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        topSkills = self.profileObj.skill_set.exclude(description__exact="")
        otherSkills = self.profileObj.skill_set.filter(description="")

        context = {
            'profile': self.profileObj,
            'topSkills': topSkills,
            'otherSkills': otherSkills
        }
        return render(request, self.template_name, context)

# ------------------Account Read & Update ------------------------------
class UserAccountView(LoginRequiredMixin, View):
    template_name = 'users/account.html'

    def get(self, request):
        profile = request.user.profile

        skills = profile.skill_set.all()
        projects = profile.project_set.all()

        context = {
            'profile': profile,
            'skills': skills,
            'projects': projects,
        }
        return render(request, self.template_name, context)


class UserEditAccountView(LoginRequiredMixin, View):
    template_name = 'users/profile-form.html'
    form_class = ProfileForm
    def dispatch(self, request, *args, **kwargs):
        self.profile = request.user.profile
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class(instance=self.profile)
        context = {
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES, instance=self.profile)
        if form.is_valid():
            form.save()

            return redirect('account')
        else:
            context = {
                'form': form,
            }
            return render(request, self.template_name, context)

# ------------------Skill Create & Update Delete ------------------------
class SkillCreateView(LoginRequiredMixin, View):
    template_name = 'users/skill-form.html'
    form_class = SkillForm

    def get(self, request):
        form = self.form_class()
        context = {'form': form,}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = request.user.profile
            skill.save()

            messages.success(request, 'Skill was successfully added')
            return redirect('account')

        context = {
            'form': form,
        }
        return render(request, self.template_name, context)


class SkillUpdateView(LoginRequiredMixin, View):
    template_name = 'users/skill-form.html'
    form_class = SkillForm

    def dispatch(self, request, *args, **kwargs):
        profile = request.user.profile
        self.skill = profile.skill_set.get(id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.skill)

        context = {'form': form,}
        return render(request, 'users/skill-form.html', context)
    
    def post(self, request, *args, **kwargs):
        form = SkillForm(request.POST, instance=self.skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill was successfully updated')
            return redirect('account')
        
        else:
            context = {'form': form,}
            return render(request, 'users/skill-form.html', context)
        

class SkillDeleteView(LoginRequiredMixin, View):
    template_name = 'users/delete-template.html'

    def dispatch(self, request, *args, **kwargs):
        profile = request.user.profile
        self.skill = profile.skill_set.get(id=kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        context = {'object': self.skill,}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.skill.delete()
        messages.success(request, 'Skill deleted')
        return redirect('account')

# ------------------Inbox Create & Update Delete ------------------------
class InboxView(LoginRequiredMixin, View):
    template_name = 'users/inbox.html'
    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        messageRequests = profile.messages.all()
        unreadCount = messageRequests.filter(is_read=False).count()

        context = {
            'messageRequests': messageRequests,
            'inreadCount': unreadCount,
        }
        return render(request, self.template_name, context)    


class MessageView(LoginRequiredMixin, View):
    template_name = 'users/message.html'
    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        message = profile.messages.get(id=kwargs['pk'])
        if message.is_read == False:
            message.is_read = True
            message.save()

        context = {'message': message,}
        return render(request, 'users/message.html', context)


class MessageCreateView(View):
    template_name = 'users/message-form.html'
    form_class = MessageForm

    def dispatch(self, request, *args, **kwargs):
        self.recipient = Profile.objects.get(id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {
            'form': form,
            'recipient': self.recipient,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        try:
            profile = request.user.profile
        except:
            profile = None

        if form.is_valid():
            message = form.save(commit=False)
            message.sender = profile
            message.recipient = self.recipient
            if profile:
                message.name = profile.name
                message.email = profile.email

            message.save()
            
            messages.success(request, 'Your message was successfully sent.')
            return redirect('single-profile', pk=self.recipient.id)

        else:
            context = {
                'form': form,
                'recipient': self.recipient,
            }
            return render(request, self.template_name, context)
