from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Account(models.Model):
    class Meta:
        permissions = (
            ("play", "Can play in the casino"),
        )

    OPENING_BALANCE = 5000
    # This field is required.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    wallet = models.TextField(blank=True)
    agreed_to_rules = models.BooleanField(default=True)
    bankroll = models.FloatField(default=OPENING_BALANCE)
    bids = models.FloatField(default=0)
    won = models.FloatField(default=0)
    score  = models.FloatField(default=0)
    @classmethod
    def open(cls, email, username, password, **kwa):
        user = User.objects.create_user(username, email, password)
        account = user.get_profile()
        AccountLine(entry_type=('accounted opened with %f' % account.bankroll),
                    account=account,
                    amount=account.bankroll,
                    bankroll=account.bankroll).save()
        return account

    def bid(self, game, amount):
        self.bankroll -= amount
        self.bids += amount
        self.score = self.won / self.bids
        AccountLine.objects.create(entry_type='%s bid %.0f' % (game, amount),
                    account=self,
                    amount=-amount,
                    bankroll=self.bankroll)
        self.save()
        return self

    def win(self, game, amount, bid, bid_returned=0):
        message = '%s bid %.0f, won %.0f' % (game, bid, amount)
        if bid_returned:
            message += '+%f' % bid_returned
            self.bankroll += bid_returned
        self.won += amount
        self.bankroll += amount
        self.score = self.won / self.bids
        AccountLine.objects.create(entry_type=message,
                    account=self,
                    amount=amount,
                    bankroll=self.bankroll).save()
        self.save()
        return amount

    def buy(self, amount):
        self.bankroll += amount
        AccountLine(entry_type='bought',
                    account=self,
                    amount=amount,
                    bankroll = self.bankroll).save()
        self.save()
        return self

class AccountLine(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, auto_created=True)
    entry_type = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    bankroll = models.FloatField()


