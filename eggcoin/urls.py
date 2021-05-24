from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_peer',views.new_peer,name="new_peer"),
    path('new_transaction',views.new_transaction,name="new_transaction"),
    path('new_block',views.new_block,name="new_block"),
    path('blockchain',views.blockchain_response,name="blockchain"),path('mine',views.mine,name="mine"),
    path('make_transaction',views.make_transaction,name="make_transaction"),
    path('transaction_form',views.transaction_form,name="transaction_form"),
    path('balance',views.balance,name="balance"),
    path('public_key',views.public_key,name="public_key")
]