from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from inventory.api import serializers
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem,Return,InventoryHistory,AuditLog



class ItemTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Werehouse", password="1234")
        self.token = Token.objects.create(user = self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.item = Item.objects.create(
            name="Soda",
            description="fanta soda",
            unit="kilogram"
        )
    
    
    def test_item_create(self):
        data ={
            "name":"Water",
            "description":"white water",
            "unit":"kilogram"
        }
        response = self.client.post(reverse('items-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_item_list(self):
        response = self.client.get(reverse('items-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_item_ind(self):
        response = self.client.get(reverse('item-detail', args=(self.item.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
class PurchaseTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Werehouse", password="1234")
        self.token = Token.objects.create(user = self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.item = Item.objects.create(
            name="Soda",
            description="fanta soda",
            unit="kilogram"
        )
        self.purchase = Purchase.objects.create(
            item=self.item,
            quantity="20",
            price_per_unit=10000,
            expiration_date="2025-10-10"
        )
        
        
    def test_purchase_create(self):
        data = {
            "item":self.item.id,
            "quantity":"20",
            "price_per_unit":10000,
            "expiration_date":"2025-10-10"
        }
        response = self.client.post(reverse('purchase-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_purchase_list(self):
        response = self.client.get(reverse('purchase-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_purchase_ind(self):
        response = self.client.get(reverse('purchase-detail', args=(self.purchase.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)