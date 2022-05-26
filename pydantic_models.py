from pydantic import BaseModel


class OfferGetModel(BaseModel):
    ntfId: int
    userId: int


class OfferResponseModel(BaseModel):
    ntfId: int
    userId: int
    offerId: int

    class Config:
        orm_mode = True


class AcceptModel(BaseModel):
    offerId: int
    nftId: int
    userId: int


class BattleModel(BaseModel):
    battleId: int
    offerUserId: int
    acceptUserId: int
    offerId: int
    acceptId: int
    healthOfferUserId: int
    healthAcceptUserId: int

    class Config:
        orm_mode = True


class BattleStartModel(BaseModel):
    offerId: int
    acceptId: int

    class Config:
        orm_mode = True


class BattleRespModel(BaseModel):
    battleId: int
    offerId: int
    acceptId: int

    class Config:
        orm_mode = True


class BattleMoveModel(BaseModel):
    userId: int
    battleId: int
    choice: int
    round: int

    class Config:
        orm_mode = True
