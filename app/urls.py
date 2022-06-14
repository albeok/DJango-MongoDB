from django.urls import path
from .views import homepage, json_pending_orders_view, profit, MarketOrderCreateView, match

urlpatterns = [
    path("", homepage, name="homepage"),
    path("json_pending_orders/", json_pending_orders_view, name="json_pending_orders"),
    path("profit/", profit, name="profit"),
    path("market_order/", MarketOrderCreateView.as_view(), name="market_order"),
    path("market_order/match/", match, name="match"),
    
]