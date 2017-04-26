from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

from .forms import RegistrationForm, YearForm, MonthForm, StashForm
from .models import Profile, Stash, Month, Year

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
    """Creates new or updates existing Year, Month and Stash objects."""
    userProfile = Profile.objects.get(user=request.user)
    stashNamesNumber = len(userProfile.stashNames.split('\n'))
    StashFormSet = modelformset_factory(Stash,
                                        form=StashForm,
                                        extra=stashNamesNumber - 1)
    if request.method == 'POST':
        yearForm = YearForm(request.POST)
        monthForm = MonthForm(request.POST)
        formset = StashFormSet(request.POST)
        if yearForm.is_valid() and monthForm.is_valid() and formset.is_valid():
            # Gets or creates Year object if does not exist yet.
            if Year.objects.filter(user=request.user,
                                   number=yearForm.cleaned_data['number']).exists():
                yearObj = Year.objects.get(user=request.user,
                                           number=yearForm.cleaned_data['number'])
            else:
                yearObj = Year(user=request.user, number=yearForm.cleaned_data['number'])
                yearObj.save()
            # Gets or creates Month object if does not exist yet.
            if Month.objects.filter(year=yearObj,
                                    name=monthForm.cleaned_data['name']).exists():
                monthObj = Month.objects.get(year=yearObj,
                                             name=monthForm.cleaned_data['name'])
            else:
                monthObj = Month(year=yearObj, name=monthForm.cleaned_data['name'])
                monthObj.save()
            # Updates or creates Stash objects.
            stashList = formset.save(commit=False)
            updatedCounter = 0
            addedCounter =0
            for stash in stashList:
                if Stash.objects.filter(month=monthObj, name=stash.name).exists():
                    stashToUpdate = Stash.objects.get(month=monthObj, name=stash.name)
                    stashToUpdate.amount = stash.amount
                    stashToUpdate.save()
                    updatedCounter += 1
                else:
                    stash.month = monthObj
                    stash.save()
                    addedCounter += 1

            templateText = '{} entries updated, {} entries added for {}.'.format(
                updatedCounter,
                addedCounter,
                monthObj
            )
            return render(request,
                          'yourFinance/success.html',
                          {'templateText': templateText,})

    yearForm = YearForm()
    monthForm = MonthForm()
    formset = StashFormSet(queryset=Stash.objects.none(),
                           initial=make_initial_list('name',
                                                     userProfile.stashNames))
    return render(request, 'yourFinance/add_data.html',
                  {'yearForm': yearForm, 'monthForm': monthForm, 'formset': formset})

@login_required
def view_data(request):
    return render(request,
                  'yourFinance/view_data.html',
                  {'years': Year.objects.filter(user=request.user)})