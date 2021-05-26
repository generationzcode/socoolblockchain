from django.db import models

# Create your models here.
class Block_chain(models.Model):
  timestamp = models.CharField(max_length=100)
  previous_hash = models.CharField(max_length=60)
  nonce = models.TextField()
  transactions = models.TextField()
  pub_date = models.DateTimeField('date published')
class unspent_coins(models.Model):
  owner_public_key_p1 = models.CharField(max_length=1000)
  owner_public_key_p2 = models.CharField(max_length=10)
  hash = models.CharField(max_length=200)
  amount = models.CharField(max_length=10)
  signature = models.CharField(max_length=1000)
  pub_date = models.DateTimeField('date published')
class owned_coins(models.Model):
  owner_public_key_p1 = models.CharField(max_length=1000)
  owner_public_key_p2 = models.CharField(max_length=10)
  hash = models.CharField(max_length=200)
  amount = models.CharField(max_length=10)
  signature = models.CharField(max_length=1000)
  pub_date = models.DateTimeField('date published')