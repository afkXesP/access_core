from django.urls import path

from . import views


urlpatterns = [
    path('orders/', views.OrdersView.as_view()),
    path('products/', views.ProductsView.as_view()),
    path('reports/', views.ReportsView.as_view()),
]
