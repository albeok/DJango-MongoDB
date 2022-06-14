# from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Wallet, Order
from .forms import PlaceOrderForm

def homepage(request):
    return render(request, "app/homepage.html")

@login_required
def match(request):
    buy_orders = Order.objects.filter(status='pending', type='buy').order_by('profile')
    sell_orders = Order.objects.filter(status='pending', type='sell').order_by('-profile')
    buyer = []
    seller = []
    if buy_orders.exists() and sell_orders.exists():
        i = 0
        greater_buy_order = buy_orders[i] 
        lower_sell_order = sell_orders[i]
        if greater_buy_order.profile.belongs_to == lower_sell_order.profile.belongs_to: 
            i += 1
        greater_buy_order = buy_orders[i] 
        lower_sell_order = sell_orders[i]
        if greater_buy_order.profile.belongs_to != lower_sell_order.profile.belongs_to:
            wallet_buyer = Wallet.objects.get(belongs_to=greater_buy_order.profile.belongs_to)
            wallet_seller = Wallet.objects.get(belongs_to=lower_sell_order.profile.belongs_to)
            if wallet_buyer.usd_balance >= lower_sell_order.price * lower_sell_order.quantity:
                wallet_buyer.usd_balance -= lower_sell_order.price * lower_sell_order.quantity
                wallet_buyer.btc_balance += lower_sell_order.quantity
                wallet_buyer.save()
                greater_buy_order.status = "completed"
                greater_buy_order.save()
                wallet_seller.usd_balance += greater_buy_order.price * greater_buy_order.quantity
                wallet_seller.btc_balance -= lower_sell_order.quantity
                wallet_seller.save()
                lower_sell_order.status = "completed"
                lower_sell_order.save()
            dict_b = {
                "id": str(wallet_buyer._id),
                "belongs_to": str(wallet_buyer.belongs_to),
                }
            buyer.append(dict_b)
            dict_s = {
                "id": str(wallet_seller._id),
                "belongs_to": str(wallet_seller.belongs_to),
                }
            seller.append(dict_s)
        json_r = {"Exchange between these two wallets":{"wallet_buyer": buyer, "wallet_seller": seller}}
        return JsonResponse(json_r)
    return render(request, "app/match.html")

@login_required
def profit(request):
    current_profit = Wallet.objects.get(belongs_to=request.user)
    dict_profit = {
            "id": str(current_profit._id),
            "belongs_to": str(current_profit.belongs_to),
            "btc_balance": current_profit.btc_balance,
            "usd_balance": current_profit.usd_balance,
        }
    all_transactions = Order.objects.filter(profile=current_profit).order_by("-datetime")
    if all_transactions.exists():
        all_transactions_list = []
        for transaction in all_transactions:
            transaction = {
                'order_id': str(transaction._id),
                'profile': str(transaction.profile),
                'datetime': transaction.datetime,
                'price': transaction.price,
                'quantity': transaction.quantity,
                'status': transaction.status,
                'type': transaction.type,
                }
            all_transactions_list.append(transaction)
        json_response = {"This is your wallet right now": dict_profit, "This is the complete history of all your transactions": all_transactions_list}
        return JsonResponse(json_response)
    return HttpResponse("<h1>You've never placed an order. Start it now!</h1>")
    
@login_required
def json_pending_orders_view(request):
    pending_orders = Order.objects.filter(status='pending').order_by('-datetime')
    buy_orders = []
    sell_orders = []
    for order in pending_orders:
        order = {
            'order_id': str(order._id),
            'profile': str(order.profile),
            'datetime': order.datetime,
            'price': order.price,
            'quantity': order.quantity,
            'status': order.status,
            'type': order.type,
            }
        if order.get("type") == "buy":
            buy_orders.append(order)
        elif order.get("type") == "sell":
            sell_orders.append(order)
    json_orders = {"pending_orders": {"buy_orders": buy_orders, "sell_orders": sell_orders}}
    return JsonResponse(json_orders)

class MarketOrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = "app/market_order.html"
    form_class = PlaceOrderForm
    success_url = "match/"

    def get_form_kwargs(self):
        kwargs = super(MarketOrderCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.profile = self.request.user.wallet
        return super().form_valid(form) 
    