from django import forms
from app.models import Wallet, Order

class PlaceOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('price', 'quantity', 'type')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PlaceOrderForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        price = self.cleaned_data['price']
        quantity = self.cleaned_data['quantity']
        type = self.cleaned_data['type']
        wallet_profile = Wallet.objects.get(belongs_to=self.request.user)
        usd_balance_wallet_profile = wallet_profile.usd_balance
        btc_balance_wallet_profile = wallet_profile.btc_balance
        if price <= 0:
            raise forms.ValidationError("Price must be greater than 0")
        elif quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than 0")
        elif price * quantity > usd_balance_wallet_profile and type == "buy":
            raise forms.ValidationError("You don't have enough money")
        elif quantity > btc_balance_wallet_profile and type == "sell":
            raise forms.ValidationError("You don't have enough Bitcoins")


