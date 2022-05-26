from tortoise.models import Model
from tortoise import fields


class Offer(Model):
    offerId = fields.IntField(pk=True)
    userId = fields.IntField()
    ntfId = fields.IntField()

    def __str__(self):
        return f"{self.userId}"


class Accept(Model):
    acceptId = fields.IntField(pk=True)
    userId = fields.IntField()
    nftId = fields.IntField()
    offer = fields.ForeignKeyField("models.Offer", related_name="accepts", on_delete=fields.CASCADE)

    def __str__(self):
        return f"{self.acceptId}"


class Battle(Model):
    battleId = fields.IntField(pk=True, unique=True)
    offerUserId = fields.IntField()
    acceptUserId = fields.IntField()
    offerId = fields.IntField()
    acceptId = fields.IntField()
    healthOfferUserId = fields.IntField(default=100)
    healthAcceptUserId = fields.IntField(default=100)

    def __str__(self):
        return f"{self.battleId}"


class BattlesLogs(Model):
    battleLogId = fields.IntField(pk=True)
    battleId = fields.IntField()
    userId = fields.IntField()
    choice = fields.IntField()
    round = fields.IntField()

    def __str__(self):
        return f"|||battleId: {self.battleId}|userId: {self.userId}|choice: {self.choice}|round: {self.round}|||"
