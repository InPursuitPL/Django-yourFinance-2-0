from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

monthsList = ['Jan', 'Feb', 'Mar', 'Apr',
              'May', 'Jun', 'Jul', 'Aug',
              'Sep', 'Oct', 'Nov', 'Dec']

class Year(models.Model):
    user = models.ForeignKey(User)
    number = models.DecimalField(max_digits=4,
                                 decimal_places=0,
                                 verbose_name='Year')

    def __str__(self):
        return '{}'.format(self.number)

    def get_ordered_months(self):
        """
        Provides ordered list of Month objects
        for this Year object.
        """
        monthsObjList = []
        for month in monthsList:
            for obj in self.month_set.all():
                if obj.name == month:
                    monthsObjList.append(obj)
        return monthsObjList


class Month(models.Model):
    NAME_CHOICES = (
        ('Jan', 'January'),
        ('Feb', 'February'),
        ('Mar', 'March'),
        ('Apr', 'April'),
        ('May', 'May'),
        ('Jun', 'June'),
        ('Jul', 'July'),
        ('Aug', 'August'),
        ('Sept', 'September'),
        ('Oct', 'October'),
        ('Nov', 'November'),
        ('Dec', 'December')
    )
    year = models.ForeignKey(Year)
    name = models.CharField(choices=NAME_CHOICES,
                            max_length=10,
                            verbose_name='Month name')

    def __str__(self):
        return '{} {}'.format(self.year, self.name)


class Stash(models.Model):
    month = models.ForeignKey(Month)
    name = models.CharField(max_length=20, verbose_name='Money deposition place')
    amount = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return '{} {} {}'.format(self.month, self.name, self.amount)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stashNames = models.TextField(default='Bank account\nSavings\nWallet\nOthers\n')
    costNames = models.TextField(default='Rent and other charges\nTransportation\n'
                                         'Clothes\nFood\nHobby\nOthers\n')
    existenceLevel = models.DecimalField(verbose_name='Existence level monthly cost',
                                         default=1500.00,
                                         max_digits=8,
                                         decimal_places=2)
    minimalLevel = models.DecimalField(verbose_name='Minimal level monthly cost',
                                       default=2000.00,
                                       max_digits=8,
                                       decimal_places=2)
    standardLevel = models.DecimalField(verbose_name='Standard level monthly cost',
                                        default=3000.00,
                                        max_digits=8,
                                        decimal_places=2)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
