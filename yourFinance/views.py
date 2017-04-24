from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

from .forms import RegistrationForm, YearForm, MonthForm, StashForm
from .models import Profile, Stash

def make_initial_list(elementName, choicesString):
    """Helper function to make initial list in formset."""
    list = []
    choicesList = choicesString.split('\n')
    for i, elem in enumerate(choicesList):
        if choicesList[i] != '':
            list.append({elementName:  choicesList[i]})
    return list

def index(request):
    return render(request, 'yourFinance/index.html')

def register_page(request):
    """Page for new user registration."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'])
            return render(request, 'registration/register_success.html',
                          {'user': form.cleaned_data['username']})
        else:
            return render(request, 'registration/register.html', {'form': form})
    form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def add_data(request):
    userProfile = Profile.objects.get(user=request.user)
    stashNamesNumber = len(userProfile.stashNames.split('\n'))
    StashFormSet = modelformset_factory(Stash,
                                        form=StashForm,
                                        extra=stashNamesNumber - 1)
    yearForm = YearForm()
    monthForm = MonthForm()
    formset = StashFormSet(queryset=Stash.objects.none(),
                           initial=make_initial_list('name',
                                                     userProfile.stashNames))
    return render(request, 'yourFinance/add_data.html',
                  {'yearForm': yearForm, 'monthForm': monthForm, 'formset': formset})