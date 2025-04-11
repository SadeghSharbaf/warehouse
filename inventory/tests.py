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
        self.export_receipt_item1 =ReceiptItem.objects.create(receipt=self.export_receipt, purchase=self.purchase, quantity=10)
        self.export_receipt_item2 =ReceiptItem.objects.create(receipt=self.export_receipt, purchase=self.purchase, quantity=5)
        
        self.import_receipt = Receipt.objects.create(type=Receipt.IMPORT)
        self.import_receipt_item1 = ReceiptItem.objects.create(
        receipt=self.import_receipt,
        purchase=self.purchase,
        quantity=5
    )
        self.import_receipt_item2 = ReceiptItem.objects.create(
        receipt=self.import_receipt,
        purchase=self.purchase,
        quantity=4
    )

        
    
    def test_export_return_create(self):
        data = {
            "receipt_item" : self.export_receipt_item1.id,
            "quantity_returned" : 5
        }
        self.purchase.quantity -= self.export_receipt_item1.quantity
        self.purchase.save()
        response = self.client.post(reverse('return-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Return.objects.count(), 1)
        self.assertEqual(Return.objects.first().quantity_returned, 5)
        
        inventory = Inventory.objects.get(item=self.item)
        self.assertEqual(inventory.total_quantity, 35)
        
        self.purchase.refresh_from_db()
        self.assertEqual(self.purchase.quantity, 10)
        
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
            "receipt_item" : self.import_receipt_item1.id,
            "quantity_returned" : 3
        }
        
        initial_return_count = Return.objects.filter(receipt_item=self.import_receipt_item1).count()
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
        
        self.import_receipt_item1.refresh_from_db()
        self.assertEqual(self.import_receipt_item1.quantity, 2)
        
        self.assertEqual(InventoryHistory.objects.count(), 1)
        self.assertEqual(AuditLog.objects.count(), 1)
        
        
    def test_bulk_export_return_create(self):
        data = [
            {
            "receipt_item" : self.export_receipt_item1.id,
            "quantity_returned" : 3
            },
            {
            "receipt_item" : self.export_receipt_item2.id,
            "quantity_returned" : 2
            }
        ]
        
        self.purchase.quantity -= (self.export_receipt_item1.quantity + self.export_receipt_item2.quantity)
        self.purchase.save()
        
        response = self.client.post(reverse('return-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(Return.objects.count(), 2)
        
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.total_quantity, 35)
        self.purchase.refresh_from_db()
        self.assertEqual(self.purchase.quantity, 5)

        
        self.assertEqual(InventoryHistory.objects.count(), 2)
        self.assertEqual(AuditLog.objects.count(), 2)
        
        
    def test_bulk_import_return_create(self):
        data = [
            {
            "receipt_item" : self.import_receipt_item1.id,
            "quantity_returned" : 3
            },
            {
            "receipt_item" : self.import_receipt_item2.id,
            "quantity_returned" : 2
            }
        ]
        
        self.purchase.quantity += (self.import_receipt_item1.quantity + self.import_receipt_item2.quantity)
        self.purchase.save()
        
        self.inventory.total_quantity += (self.import_receipt_item1.quantity + self.import_receipt_item2.quantity)
        self.inventory.save()
        
        response = self.client.post(reverse('return-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(Return.objects.count(), 2)
        
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.total_quantity, 30+9-5)
        self.purchase.refresh_from_db()
        self.assertEqual(self.purchase.quantity, 19)

        
        self.assertEqual(InventoryHistory.objects.count(), 2)
        self.assertEqual(AuditLog.objects.count(), 2)
        
        
    def test_export_return_quantity(self):
        data = {
            "receipt_item": self.export_receipt_item1.id ,
            "quantity_returned": self.export_receipt_item1.quantity + 1
        }
        
        response = self.client.post(reverse('return-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
    def test_return_list(self):
        response = self.client.get(reverse('return-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        

class ReturnHistoryTestCase(APITestCase):
    
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
            quantity=20,
            price_per_unit=1000,
            expiration_date=date(2025, 10, 30)
        )
        self.inventory = Inventory.objects.create(item=self.item , total_quantity = 20)
        self.export_receipt = Receipt.objects.create(type = Receipt.EXPORT)
        self.import_receipt = Receipt.objects.create(type=Receipt.IMPORT)
        self.export_receipt_item =ReceiptItem.objects.create(
            receipt=self.export_receipt, 
            purchase=self.purchase,
            quantity=5)
        self.import_receipt_item = ReceiptItem.objects.create(
            receipt=self.import_receipt,
            purchase=self.purchase,
            quantity=5
        )
        self.return1 = Return.objects.create(receipt_item=self.export_receipt_item, quantity_returned=2, return_date=date.today())
        self.return2 = Return.objects.create(receipt_item=self.import_receipt_item, quantity_returned=3, return_date=date.today())
        
        
    def test_returns_history(self):
        response = self.client.get(reverse("return-history"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    
    def test_returns_history_filter(self):
        url = reverse("return-history") + "?receipt_item__receipt__type=export"
        response = self.client.get(url)
        print("Response data for import returns H:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["receipt_item"], self.export_receipt_item.id)

        url = reverse("return-history") + "?receipt_item__receipt__type=import"
        response = self.client.get(url)
        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["receipt_item"], self.import_receipt_item.id)
        
    def test_filter_by_return_date(self):
        today = date.today()
        url = reverse("return-history") + f"?return_date={today}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_returns_ind(self):
        response = self.client.get(reverse('return-detail', args=(self.return1.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
        
class ExpiringSoonTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="Sadeghh", password="1234")
        self.token = Token.objects.create(user = self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.item = Item.objects.create(
            name="Soda",
            description="fanta soda",
            unit="kilogram"
        )
        self.purchase_soon = Purchase.objects.create(
            item=self.item,
            quantity=10,
            price_per_unit=1000,
            expiration_date=date(2025, 4, 15)
        )
        self.purchase_later = Purchase.objects.create(
            item=self.item,
            quantity=20,
            price_per_unit=1500,
            expiration_date=date(2025, 4, 20)
        )
        self.purchase_far = Purchase.objects.create(
            item=self.item,
            quantity=30,
            price_per_unit=2000,
            expiration_date=date(2025, 10, 30)
        )
        
        
    def test_expire_soon(self):
        url = reverse('expiring') + "?days=10"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["id"], self.purchase_soon.id)
        self.assertEqual(response.data[1]["id"], self.purchase_later.id)
        
        
        
class AuditLogListTestCase(APITestCase):
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username="admin", password="adminpassword")
        self.token = Token.objects.create(user = self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_user.auth_token.key)
        self.normal_user = User.objects.create_user(username="user", password="userpassword")
        
        self.item = Item.objects.create(
            name="Soda",
            description="fanta soda",
            unit="kilogram"
        )
        
        self.export_receipt = Receipt.objects.create(type = Receipt.EXPORT)
        self.import_receipt = Receipt.objects.create(type = Receipt.IMPORT)
        
        self.audit_log1 = AuditLog.objects.create(action="import", item=self.item,
            user=self.admin_user, timestamp=date(2025, 8, 30), quantity = 10, receipt = self.import_receipt)
        self.audit_log2 = AuditLog.objects.create(action="export", item=self.item,
            user=self.admin_user, timestamp=date(2025, 7, 30), quantity = 20, receipt = self.import_receipt)
        self.audit_log3 = AuditLog.objects.create(action="return", item=self.item,
            user=self.normal_user, timestamp=date(2025, 10, 30), quantity = 30, receipt = self.export_receipt)
        
        
    def test_audit_log_list_admin_access(self):
        response = self.client.get(reverse('audit-trail'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        
    def test_audit_log_list_normaluser(self):
        self.token = Token.objects.create(user = self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.normal_user.auth_token.key)
        response = self.client.get(reverse('audit-trail'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    
    def test_audit_log_filter_action(self):
        url = reverse("audit-trail") + "?action=import"
        response = self.client.get(url)
        self.assertEqual(response.status_code ,status.HTTP_200_OK)
        self.assertEqual(response.data[0]["action"], "import")