from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from inventory.api import serializers
from inventory.models import Item,Purchase,Inventory,Receipt,ReceiptItem,Return,InventoryHistory,AuditLog
from inventory import models
from datetime import date
from django.db.models import Sum




class ItemTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Sadeghh", password="1234")
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
            "unit":"liter"
        }
        response = self.client.post(reverse('items-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
    def test_item_list(self):
        response = self.client.get(reverse('items-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_item_ind(self):
        response = self.client.get(reverse('item-detail', args=(self.item.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_item_update(self):
        data = {
        "name": "Updated Soda",
        "description": "Updated desc",
        "unit": "liter"
    }
        response = self.client.put(reverse('item-detail', args=(self.item.id,)),data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Updated Soda')
        
        
    def test_item_delete(self):
        response = self.client.delete(reverse('item-detail', args=(self.item.id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())


        
class PurchaseTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Sadeghh", password="1234")
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
        self.assertEqual(models.Purchase.objects.count(), 1)
        self.assertEqual(models.Purchase.objects.get().item.name, 'Soda')
        
        
    def test_purchase_update(self):
        data = {
            "item": self.item.id,
            "quantity": "50",
            "price_per_unit": 15000,
            "expiration_date": "2025-12-12"
        }
        response = self.client.put(reverse('purchase-detail', args=(self.purchase.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.purchase.refresh_from_db()
        self.assertEqual(self.purchase.quantity,50)
        self.assertEqual(self.purchase.price_per_unit, 15000)
        
        
    def test_purchase_delete(self):
        response = self.client.delete(reverse('purchase-detail', args=(self.purchase.id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Purchase.objects.filter(id=self.purchase.id).exists())
        
        
        
class SummaryTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Sadeghh", password="1234")
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
        
        
    def test_summary_list(self):
        response = self.client.get(reverse('summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
        
class ReceiptTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Sadeghh", password="1234")
        self.token = Token.objects.create(user = self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.item = Item.objects.create(
            name="Soda",
            description="fanta soda",
            unit="kilogram"
        )
        self.purchase = Purchase.objects.create(
            item=self.item,
            quantity=100,
            price_per_unit=5000,
            expiration_date="2025-10-31"
        )
        self.receipt = Receipt.objects.create(
            type="import",
            optional_notes="none"
        )
        
        
    def test_receipt_create(self):
        data = {
            "type": "export",
            "creation_date": "2025-04-10"
        }
        
        response = self.client.post(reverse('receipt-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Receipt.objects.count(), 2)
        
        
    def test_receipt_list(self):
        response = self.client.get(reverse('receipt-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_receipt_retrieve(self):
        response = self.client.get(reverse('receipt-detail', args=(self.receipt.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.receipt.id)
        
        
    def test_receipt_update(self):
        data = {
            "type": "export",
            "creation_date": "2025-04-05"
        }
        response = self.client.put(reverse('receipt-detail', args=(self.receipt.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.receipt.refresh_from_db()
        self.assertEqual(self.receipt.type, "export")
        
        
    def test_receipt_delete(self):
        response = self.client.delete(reverse('receipt-detail', args=(self.receipt.id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Receipt.objects.filter(id=self.receipt.id).exists())
        
      
        
class ReceiptItemTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Sadeghh", password="1234")
        self.token = Token.objects.create(user = self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.item = Item.objects.create(
            name="Soda",
            description="fanta soda",
            unit="kilogram"
        )
        self.purchase1 = Purchase.objects.create(
            item=self.item,
            quantity=10,
            price_per_unit=5000,
            expiration_date=date(2025, 10, 30)
        )
        self.purchase2 = Purchase.objects.create(
            item=self.item,
            quantity=20,
            price_per_unit=6000,
            expiration_date=date(2025, 11, 30)
        )
        self.receipt_import = Receipt.objects.create(type=Receipt.IMPORT,optional_notes="none")
        self.receipt_export = Receipt.objects.create(type=Receipt.EXPORT,optional_notes="nooone")
        
        self.inventory = Inventory.objects.create(item=self.item, total_quantity=15)
        
        self.receipt_item_import = ReceiptItem.objects.create(
            receipt=self.receipt_import,
            purchase=self.purchase1,
            quantity=3
        )
        self.receipt_item_export = ReceiptItem.objects.create(
            receipt=self.receipt_export,
            purchase=self.purchase2,
            quantity=5
        )
        
    
    def test_receipt_item_import_create(self):
        data = {
            "receipt": self.receipt_import.id,
            "purchase": self.purchase1.id,
            "quantity": 2
        }
        response = self.client.post(reverse('receipt-item-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inventory.objects.get(item=self.item).total_quantity, 17)
        
        
    def test_receipt_item_export_create(self):
        data = {
            "receipt": self.receipt_export.id,
            "purchase": self.purchase1.id,
            "quantity": 5
        }
        response = self.client.post(reverse('receipt-item-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inventory.objects.get(item=self.item).total_quantity, 10)
        
        
    def test_receipt_item_bulk_import_create(self):
        data = [
            {
                "receipt": self.receipt_import.id,
                "purchase": self.purchase1.id,
                "quantity": 2
            },
            {
                "receipt": self.receipt_import.id,
                "purchase": self.purchase2.id,
                "quantity": 3
            }
        ]
        response = self.client.post(reverse('receipt-item-list-create'), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(Inventory.objects.get(item=self.item).total_quantity, 20)
        
        
    def test_receipt_item_bulk_export_create(self):
        data = [
            {
                "receipt": self.receipt_export.id,
                "purchase": self.purchase1.id,
                "quantity": 2
            },
            {
                "receipt": self.receipt_export.id,
                "purchase": self.purchase2.id,
                "quantity": 4
            }
        ]
        response = self.client.post(reverse('receipt-item-list-create'), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(Inventory.objects.get(item=self.item).total_quantity, 9)
        
        
    def test_receipt_item_list(self):
        response = self.client.get(reverse('receipt-item-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data)>=1)
        
        
    def test_receipt_item_detail_list(self):
        response_import = self.client.get(reverse('receipt-item-detail', args=[self.receipt_item_import.id]))
        self.assertEqual(response_import.status_code, status.HTTP_200_OK)
        self.assertEqual(response_import.data["id"], self.receipt_item_import.id)

        response_export = self.client.get(reverse('receipt-item-detail', args=[self.receipt_item_export.id]))
        self.assertEqual(response_export.status_code, status.HTTP_200_OK)
        self.assertEqual(response_export.data["id"], self.receipt_item_export.id)
        
        
    def test_receipt_item_update_import(self):
        data = {
            "receipt": self.receipt_import.id,
            "purchase": self.purchase1.id,
            "quantity": 5
        }
        
        old_quantity = self.receipt_item_import.quantity
        initial_quantity = Inventory.objects.get(item=self.item).total_quantity
        
        response = self.client.put(reverse('receipt-item-detail', args=(self.receipt_item_import.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.receipt_item_import.refresh_from_db()
        self.assertEqual(self.receipt_item_import.quantity, 5)
        
        expected_quantity = initial_quantity - old_quantity + data['quantity']
        self.assertEqual(Inventory.objects.get(item=self.item).total_quantity, expected_quantity)
        
        
        
    def test_receipt_item_update_export(self):
        data = {
            "receipt": self.receipt_export.id,
            "purchase": self.purchase1.id,
            "quantity": 5
        }
        
        old_quantity = self.receipt_item_export.quantity
        initial_quantity = Inventory.objects.get(item=self.item).total_quantity
        
        response = self.client.put(reverse('receipt-item-detail', args=(self.receipt_item_export.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.receipt_item_export.refresh_from_db()
        self.assertEqual(self.receipt_item_export.quantity, 5)
        
        expected_quantity = initial_quantity + old_quantity - data["quantity"]
        #print("Initial quantity:", initial_quantity)
        #print("Old receipt quantity:", old_quantity)
        #print("New receipt quantity:", data["quantity"])
        #print("Expected:", expected_quantity)
        #print("Actual:", Inventory.objects.get(item=self.item).total_quantity)

        self.assertEqual(Inventory.objects.get(item=self.item).total_quantity, expected_quantity)
        
        
    def test_receipt_item_delete(self):
        initial_quantity = Inventory.objects.get(item=self.item).total_quantity
        
        response_import = self.client.delete(reverse('receipt-item-detail', args=(self.receipt_item_import.id,)))
        self.assertEqual(response_import.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ReceiptItem.objects.filter(id=self.receipt_item_import.id).exists())
        
        expected_quantity_after_import_delete = initial_quantity - self.receipt_item_import.quantity
        self.assertEqual(Inventory.objects.get(item=self.item).total_quantity, expected_quantity_after_import_delete)
        
        
        
        current_quantity = Inventory.objects.get(item=self.item).total_quantity
        
        response_export = self.client.delete(reverse('receipt-item-detail', args=(self.receipt_item_export.id,)))
        self.assertEqual(response_export.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ReceiptItem.objects.filter(id=self.receipt_item_export.id).exists())
        
        expected_quantity_after_export_delete = current_quantity + self.receipt_item_export.quantity
        self.assertEqual(Inventory.objects.get(item=self.item).total_quantity, expected_quantity_after_export_delete)
        
        
class IvnevtoryHistoryTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Sadeghh", password="1234")
        self.token = Token.objects.create(user = self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.item = Item.objects.create(
            name="Soda",
            description="fanta soda",
            unit="kilogram"
        )
        self.purchase = Purchase.objects.create(
            item=self.item,
            quantity=10,
            price_per_unit=5000,
            expiration_date=date(2025, 10, 30)
        )
        self.receipt = Receipt.objects.create(type='import')
        self.inventory = Inventory.objects.create(item=self.item , total_quantity =10)
        self.history = InventoryHistory.objects.create(
            receipt = self.receipt,
            item = self.item,
            change_type = 'import',
            quantity_changed = 10
        )
        
        
    def test_inventoryhistory_list(self):
        response = self.client.get(reverse('inventory-history'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['quantity_changed'], 10)
        self.assertEqual(response.data[0]['change_type'],'import' )
        
        

class ReturnTesCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Sadeghh", password="1234")
        self.token = Token.objects.create(user = self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.item = Item.objects.create(
            name="Soda",
            description="fanta soda",
            unit="kilogram"
        )
        self.purchase = Purchase.objects.create(
            item=self.item,
            quantity=15,
            price_per_unit=5000,
            expiration_date=date(2025, 10, 30)
        )
        self.export_receipt = Receipt.objects.create(type = Receipt.EXPORT)
        self.inventory = Inventory.objects.create(item=self.item , total_quantity = 30)
        self.export_receipt_item =ReceiptItem.objects.create(receipt=self.export_receipt, purchase=self.purchase, quantity=10)
        
        self.import_receipt = Receipt.objects.create(type=Receipt.IMPORT)
        self.import_receipt_item = ReceiptItem.objects.create(
        receipt=self.import_receipt,
        purchase=self.purchase,
        quantity=5
    )

        
    
    def test_export_return_create(self):
        data = {
            "receipt_item" : self.export_receipt_item.id,
            "quantity_returned" : 5
        }
        self.purchase.quantity -= self.export_receipt_item.quantity
        self.purchase.save()
        response = self.client.post(reverse('return-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Return.objects.count(), 1)
        self.assertEqual(Return.objects.first().quantity_returned, 5)
        
        inventory = Inventory.objects.get(item=self.item)
        self.assertEqual(inventory.total_quantity, 35)
        
        self.purchase.refresh_from_db()
        self.assertEqual(self.purchase.quantity, 5)
        
        self.assertEqual(InventoryHistory.objects.count(), 1)
        history = InventoryHistory.objects.first()
        self.assertEqual(history.item, self.item)
        self.assertEqual(history.receipt, self.export_receipt)
        self.assertEqual(history.change_type, 'return')
        self.assertEqual(history.quantity_changed, 5)
        
        self.assertEqual(AuditLog.objects.count(), 1)
        log = AuditLog.objects.first()
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, AuditLog.RETURN)
        self.assertEqual(log.item, self.item)
        self.assertEqual(log.receipt, self.export_receipt)
        self.assertEqual(log.quantity, 5)
        
        
    def test_import_return_create(self):
        data = {
            "receipt_item" : self.import_receipt_item.id,
            "quantity_returned" : 3
        }
        
        initial_return_count = Return.objects.filter(receipt_item=self.import_receipt_item).count()
        self.assertEqual(initial_return_count, 0) 
        self.purchase.quantity += 5
        self.purchase.save()
        
        self.inventory.total_quantity +=5 
        self.inventory.save()
        
        response = self.client.post(reverse('return-list-create'), data)
        print("Request data:", data)
 


        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("Response data:", response.data)
        self.assertEqual(Return.objects.count(), 1)
        self.assertEqual(Return.objects.first().quantity_returned, 3)
        
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.total_quantity, 32)
        
        self.import_receipt_item.refresh_from_db()
        self.assertEqual(self.import_receipt_item.quantity, 2)
        
        self.assertEqual(InventoryHistory.objects.count(), 1)
        self.assertEqual(AuditLog.objects.count(), 1)