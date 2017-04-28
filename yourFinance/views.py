from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, formset_factory

from .forms import RegistrationForm, YearForm, MonthForm, \
    StashForm, NameForm, MonthlyCostsForm, MonthFullForm, \
    CostGroupsForm
from .models import Profile, Stash, Month, Year, monthsList

def make_initial_list(elementName, choicesString):
    """Helper function to make initial list in formset."""
    list = []
    choicesList = choicesString.split('\n')
    for i, elem in enumerate(choicesList):
        if choicesList[i] != '':
            list.append({elementName:  choicesList[i]})
    return list

def give_monthly_costs_information(userProfile, totalAmount):
    """
    Helper function for analyzing data.
    Returns list of strings to view in template.
    """
    monthlyCostsList = [(userProfile.existenceLevel, 'existence level'),
                        (userProfile.minimalLevel, 'minimal level'),
                        (userProfile.standardLevel, 'standard level')]
    monthlyCostsStrings = []
    for amount in monthlyCostsList:
        monthlyCostsStrings.append('Your current sum is enough for {} months'
                                   ' based on {} amount of {}.'.format(
            round(totalAmount / amount[0], 1),
            amount[0],
            amount[1]))
    return monthlyCostsStrings


def _newest_objects_set(yearObjects):
    """
    Helper function for analyzing data. Returns from nested
    for loops as soon as it finds newest Stash objects.
     """
    for yearObj in yearObjects:
        monthObjects = yearObj.get_ordered_months()
        for monthObj in reversed(monthObjects):
            if len(monthObj.stash_set.all()) > 0:
                stashObjects = monthObj.stash_set.all()
                return (stashObjects, monthObj, yearObj)

def get_previous_entries_and_total(newestYearObj, newestMonthObj, monthsList, user):
    """
        Helper function for analyzing data. Returns stashes group and total
        amount for month previous to newest or sets it to None if there
        are no data.
    """
    previousYearObj = newestYearObj
    previousTotalAmount = 0
    if newestMonthObj.name == 'Jan':
        previousYearNumber = newestYearObj.number - 1
        try:
            previousYearObj = Year.objects.get(user=user,
                                               number=previousYearNumber)
        except Year.DoesNotExist:
            previousYearObj = None
    if previousYearObj:
        previousMonthName = monthsList[monthsList.index(newestMonthObj.name)-1]
        try:
            previousMonthObj = Month.objects.get(year=previousYearObj,
                                                 name=previousMonthName)
        except Month.DoesNotExist:
            previousMonthObj = None
    if previousMonthObj:
        previousStashesGroup = previousMonthObj.stash_set.all()
        if len(previousStashesGroup) == 0:
            previousStashesGroup = None
        else:
            for stashObj in previousStashesGroup:
                previousTotalAmount += stashObj.amount
    else:
        previousStashesGroup = None
    return (previousStashesGroup, previousTotalAmount, previousMonthObj)

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
    "View User's all Year, Month and Stash objects."
    return render(request,
                  'yourFinance/view_data.html',
                  {'years': Year.objects.filter(user=request.user
                                                ).order_by('-number')})

@login_required
def edit_stash(request, pk):
    """Edit single Stash entry."""
    message = 'Here you can edit chosen data.'
    stash = get_object_or_404(Stash, pk=pk)
    # I've used here 'Easy Form Views Pattern' just to test it but i will
    # not change other views to it, as there are some edge cases where this
    # pattern will fail in an unexpected way. Explicit form seems also to
    # be more pythonic.
    form = StashForm(request.POST or None, instance=stash)
    if form.is_valid():
        form.save()
        return render(request, 'yourFinance/success.html')
    return render(request,
                  'yourFinance/edit_stash.html',
                  {'form': form, 'message': message})

@login_required
def edit_month(request, pk):
    """Edit single Month entry together with Stash objects."""
    message = 'Here you can edit chosen data.'
    month = get_object_or_404(Month, pk=pk)
    StashFormSet = modelformset_factory(Stash,
                                        form=StashForm,
                                        extra=0)
    if request.method == 'POST':
        form = MonthFullForm(request.POST)
        formset = StashFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            month.name, month.year = form.cleaned_data['name'], \
                                     form.cleaned_data['year']
            month.save()
            formset.save()
            return render(request, 'yourFinance/success.html')

    form = MonthFullForm(instance=month)
    formset = StashFormSet(queryset=Stash.objects.filter(month=month))
    return render(request,
                  'yourFinance/edit_month.html',
                  {'form': form, 'formset': formset, 'message': message})

@login_required
def delete_stash(request, pk):
    """Delete single Stash entry."""
    stash = get_object_or_404(Stash, pk=pk)
    if request.method == 'POST':
        stash.delete()
        return render(request, 'yourFinance/success.html')
    return render(request, 'yourFinance/confirm_delete.html')

@login_required
def delete_month(request, pk):
    """Delete single Month entry with Stash objects."""
    month = get_object_or_404(Month, pk=pk)
    if request.method == 'POST':
        month.delete()
        return render(request, 'yourFinance/success.html')
    return render(request, 'yourFinance/confirm_delete.html')

@login_required
def delete_year(request, pk):
    """Delete single Year entry with Month and Stash objects."""
    year = get_object_or_404(Year, pk=pk)
    if request.method == 'POST':
        year.delete()
        return render(request, 'yourFinance/success.html')
    return render(request, 'yourFinance/confirm_delete.html')

@login_required
def analyze_month(request):
    userProfile = Profile.objects.get(user=request.user)
    yearObjects = Year.objects.filter(user=request.user).order_by('-number')
    # External helper function in use to get newest objects.
    if yearObjects:
        newestStashesGroup, \
        newestMonthObj, \
        newestYearObj = _newest_objects_set(yearObjects)
    # If there are no data, returns without analyzing.
    if not yearObjects or not newestStashesGroup:
        return render(request,
                      'yourFinance/failure.html',
                      {'templateText': 'No data to analyze!'})
    totalAmount = 0
    for stashObj in newestStashesGroup:
        totalAmount += stashObj.amount
    # External function in use to collect data entries previous to
    #  newest, if exist.
    previousStashesGroup, \
    previousTotalAmount, \
    previousMonth = get_previous_entries_and_total(newestYearObj,
                                                    newestMonthObj,
                                                    monthsList,
                                                    request.user)
    # If there are any previous data, it will view it.
    if previousStashesGroup:
        arePrevious = True
        messagePrevious = 'Data from previous record: '
        previousTotalStatement = 'Total sum: {}'.format(previousTotalAmount)
        gain = totalAmount - previousTotalAmount
        if gain >= 0:
            messageGain = 'You have gained {}'.format(gain)
        else:
            messageGain = 'You have lost {}'.format(abs(gain))
    # If there are no previous data, only information about it will be visible.
    else:
        arePrevious = False
        messagePrevious = 'No previous data in database.'
    # Part to analyze for how long current sum will be enough. Uses external
    # helper function.
    monthlyCostsStrings = give_monthly_costs_information(userProfile, totalAmount)
    # Part to ask in formset and analyze expenses in cost groups.
    CostGroupsFormSet = formset_factory(CostGroupsForm, extra=0)
    afterCostsMessage = ''
    if request.method == 'POST':
        cost_groups_formset = CostGroupsFormSet(request.POST)
        if cost_groups_formset.is_valid():
            totalCosts = 0
            totalAmountAfterExpenses = float(totalAmount)
            for dictionary in cost_groups_formset.cleaned_data:
                totalCosts += dictionary['amount']
                totalAmountAfterExpenses -= dictionary['amount']
            afterCostsMessage = 'Your total current costs are {},' \
                                ' after expenses you will have {}.' \
                .format(totalCosts, totalAmountAfterExpenses)
    else:
        cost_groups_formset = CostGroupsFormSet(
            initial=make_initial_list('name', userProfile.costNames)
        )
        afterCostsMessage = ''
    templateDict = {'newestMonth': newestMonthObj,
                    'newestStashesGroup': newestStashesGroup,
                    'totalAmount': totalAmount,
                    'messagePrevious': messagePrevious,
                    'monthlyCostsStrings': monthlyCostsStrings,
                    'formset': cost_groups_formset,
                    'afterCostsMessage': afterCostsMessage
                    }
    # Added only if there were previous data before newest/required ones.
    if arePrevious:
        templateDict['previousMonth'] = previousMonth
        templateDict['previousStashesGroup'] = previousStashesGroup
        templateDict['previousTotalStatement'] = previousTotalStatement
        templateDict['messageGain'] = messageGain

    return render(request, 'yourFinance/analyze.html', templateDict)


@login_required
def configure_deposition_places(request):
    """Enables configuring user stashNames field, stored in Profile model."""
    userProfile = Profile.objects.get(user=request.user)
    StashNameFormSet = formset_factory(NameForm, extra=1)
    if request.method == 'POST':
        formset = StashNameFormSet(request.POST)
        if formset.is_valid():
            newString = ''
            for dictionary in formset.cleaned_data:
                if dictionary and not dictionary['name']=='':
                    newString += dictionary['name'] + '\n'
            userProfile.stashNames = newString
            userProfile.save()
            return render(request, 'yourFinance/success.html')
    formset = StashNameFormSet(
        initial=make_initial_list('name', userProfile.stashNames)
    )
    return render(request, 'yourFinance/configure_names.html',
                  {'formset': formset})

@login_required
def configure_monthly_costs(request):
    """
    Enables configuring user monthly cost fields,
    stored in Profile model.
    """
    userProfile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = MonthlyCostsForm(request.POST)
        if form.is_valid():
            userProfile.existenceLevel = form.cleaned_data['existenceLevel']
            userProfile.minimalLevel = form.cleaned_data['minimalLevel']
            userProfile.standardLevel = form.cleaned_data['standardLevel']
            userProfile.save()
            print(userProfile.existenceLevel)
            return render(request, 'yourFinance/success.html')
    form = MonthlyCostsForm(instance=userProfile)
    return render(request,
                  'yourFinance/configure_monthly_costs.html',
                  {'form': form})

@login_required
def configure_cost_groups(request):
    """Enables configuring user costNames field, stored in Profile model."""
    userProfile = Profile.objects.get(user=request.user)
    CostNameFormSet = formset_factory(NameForm, extra=1)
    if request.method == 'POST':
        formset = CostNameFormSet(request.POST)
        if formset.is_valid():
            newString = ''
            for dictionary in formset.cleaned_data:
                if dictionary and not dictionary['name']=='':
                    newString += dictionary['name'] + '\n'
            userProfile.costNames = newString
            userProfile.save()
            return render(request, 'yourFinance/success.html')
    formset = CostNameFormSet(
        initial=make_initial_list('name', userProfile.costNames)
    )
    return render(request, 'yourFinance/configure_names.html',
                  {'formset': formset})

