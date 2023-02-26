from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from .utils import searchProjects, paginateProjects

# Create your views here.
class ProjectsView(View):
    template_name = 'projects/projects.html'
    def get(self, request):
        projects, search_query = searchProjects(request)
        custom_range, projects = paginateProjects(request, projects, 3)
        
        context  = {
            'projects': projects,
            'search_query': search_query,
            'custom_range': custom_range
        }
        return render(request, self.template_name, context)


class ProjectView(View):
    template_name = 'projects/single-project.html'
    form_class = ReviewForm
    
    def dispatch(self, request, *args, **kwargs):
        self.project_obj = Project.objects.get(pk=kwargs['pk'])
        self.reviews = self.project_obj.review_set.all()

        return super().dispatch(request, *args, **kwargs)
    

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        context = {
            'project': self.project_obj,
            'form': form,
            'reviews': self.reviews,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.project = self.project_obj
            review.owner = request.user.profile
            review.save()
            self.project_obj.getVoteCount

            messages.success(request, 'Review successfully was submitted!')
            return redirect('single-project', pk=self.project_obj.id)
        
        else:
            context = {
                'project': self.project_obj,
                'form': form,
                'reviews': self.reviews,
            }
            return render(request, self.template_name, context)
    

class ProjectCreateView(LoginRequiredMixin, View):
    template_name = 'projects/project-form.html'
    form_class = ProjectForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        newtags = request.POST.get('newtags').replace(',',  " ").split()
        
        form = self.form_class(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user.profile
            project.save() 

            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)

            return redirect('account')
        else:
            context = {'form': form}
            return render(request, self.template_name, context)


class ProjectUpdateView(LoginRequiredMixin, View):
    template_name = 'projects/project-form.html'
    form_class = ProjectForm

    def dispatch(self, request, *args, **kwargs):
        profile = request.user.profile
        self.project_obj = profile.project_set.get(id=kwargs['pk'])
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.project_obj)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        newtags = request.POST.get('newtags').replace(',',  " ").split()
        form = self.form_class(request.POST, request.FILES, instance=self.project_obj)
        if form.is_valid():
            project = form.save(commit=False)
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)

            return redirect('account')
        else:
            context = {'form': form}
            return render(request, self.template_name, context)
        
class ProjectDeleteView(LoginRequiredMixin, View):
    template_name = 'delete-template.html'
    def dispatch(self, request, *args, **kwargs):
        profile = request.user.profile
        self.project = profile.project_set.get(id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        context = {'project': self.project}
        return render(request, 'delete-template.html', context)

    def post(self, request, *args, **kwargs):
        self.project.delete()
        return redirect('account')
