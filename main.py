import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from tortoise.contrib.fastapi import register_tortoise
from tortoise.queryset import Q

from app_models.models import Accept, Battle, BattlesLogs, Offer
from connection_manager import ConnectionManager
from game_logic import (check_winner_and_loser, damage_loser,
                        user_can_get_damage)
from pydantic_models import (AcceptGetModel, BattleMoveModel, BattleRespModel,
                             BattleStartModel, OfferGetModel,
                             OfferRespModel, AcceptModelResp)


app = FastAPI()


register_tortoise(
    app,
    db_url="sqlite://database/db.sqlite3",
    modules={"models": ["app_models.models"]},
    add_exception_handlers=True,
)


@app.post("/battles_create", status_code=201)
async def battles_create(offer_model: OfferGetModel):
    offer = await Offer.create(userId=offer_model.userId, ntfId=offer_model.ntfId)
    return {"offer": offer}


@app.get("/battles_list", status_code=200)
async def battles_list():
    offers = await Offer.all()
    offers_response = [OfferRespModel.from_orm(offer) for offer in offers]
    return {"offers": offers_response}


@app.post("/battles/accept", status_code=201)
async def battles_accept(accept_model: AcceptGetModel):
    accept = await Accept.create(
        userId=accept_model.userId,
        nftId=accept_model.nftId,
        offerId=accept_model.offerId
    )

    offer = await Offer.get(offerId=accept_model.offerId).prefetch_related('accepts')
    accept.offer = offer

    await accept.save()
    return {"accept": AcceptModelResp.from_orm(accept)}


@app.post("/battles_start", status_code=201)
async def battles_start(battle: BattleStartModel):
    offer = await Offer.get_or_none(offerId=battle.offerId).prefetch_related("accepts")
    accept = await offer.accepts.filter(acceptId=battle.acceptId).first()

    if offer is None or accept is None:
        raise HTTPException(
            status_code=409,
            detail="Accept or offer does not exists"
        )

    battle_q_for_check = await Battle.filter(acceptId=battle.acceptId, offerId=battle.offerId).exists()
    if battle_q_for_check:
        raise HTTPException(
            status_code=409,
            detail="Battle with this acceptId and offerId is already exists"
        )

    battle_resp = await Battle.create(
        offerUserId=offer.userId,
        acceptUserId=accept.userId,
        offerId=offer.offerId,
        acceptId=accept.acceptId
    )

    await offer.delete()
    return {"battle": BattleRespModel.from_orm(battle_resp)}


@app.post("/battles_move", status_code=201)
async def battles_move(battle_move: BattleMoveModel):
    last_battlelogs = await BattlesLogs.filter(battleId=battle_move.battleId)
    if len(last_battlelogs) != 0 and last_battlelogs[-1].userId == battle_move.userId:
        raise HTTPException(
            status_code=409,
            detail="Wait for another player's move"
        )

    user_in_battle = await Battle.filter(
        Q(
            Q(offerUserId=battle_move.userId),
            Q(acceptUserId=battle_move.userId),
            join_type="OR"
        )
    ).exists()
    if not user_in_battle:
        raise HTTPException(
                 status_code=409,
                 detail="You should being in battle to make move"
        )

    move_exists = await BattlesLogs.filter(
        Q(
            Q(userId=battle_move.userId),
            Q(battleId=battle_move.battleId),
            Q(choice=battle_move.choice),
            Q(round=battle_move.round),
            join_type="AND"
        )
    ).exists()
    if move_exists:
        raise HTTPException(
                 status_code=409,
                 detail="You already make this move"
        )

    await BattlesLogs.create(
        userId=battle_move.userId,
        battleId=battle_move.battleId,
        choice=battle_move.choice,
        round=battle_move.round
    )
    return {}


manager = ConnectionManager()


@app.websocket("/ws/{room_name}")
# room_name --> battleId
async def websocket_endpoint(websocket: WebSocket, room_name: int):
    await manager.connect(websocket, room_name)

    battle_id = room_name
    battle_exists = await Battle.filter(battleId=battle_id).exists()
    if not battle_exists:
        manager.remove(websocket, room_name)
        raise WebSocketDisconnect(1000)

    # list for count of logs
    used_battlelogs_count = []

    try:
        while True:
            await asyncio.sleep(2)
            battle_exists = await Battle.filter(battleId=battle_id).exists()
            if not battle_exists:
                manager.remove(websocket, room_name)
                raise WebSocketDisconnect(1000)
            room_members = (
                manager.get_members_room(room_name)
                if manager.get_members_room(room_name) is not None
                else []
            )
            if websocket not in room_members:
                print("SENDER NOT IN ROOM MEMBERS: RECONNECTING")
                await manager.connect(websocket, room_name)

            battle = await Battle.filter(battleId=battle_id).first()
            battle_moves = await BattlesLogs.filter(battleId=battle_id)
            battle_moves_count = await BattlesLogs.filter(battleId=battle_id).count()

            if battle_moves_count % 2 == 0 and battle_moves_count >= 2:
                player_move1, player_move2 = battle_moves[-1], battle_moves[-2]
                winner_id, loser_id = check_winner_and_loser(
                    BattleMoveModel.from_orm(player_move1),
                    BattleMoveModel.from_orm(player_move2)
                )

                if battle_moves_count in used_battlelogs_count:
                    continue
                used_battlelogs_count.append(battle_moves_count)

                if winner_id is not None:
                    await damage_loser(battle, loser_id)
                    data = {
                        "battles_round": {
                            f"{player_move1.userId}": player_move1.choice,
                            f"{player_move2.userId}": player_move2.choice,
                            "winner": winner_id
                        }
                    }
                else:
                    data = {
                        "battles_round": {
                            f"{player_move1.userId}": player_move1.choice,
                            f"{player_move2.userId}": player_move2.choice,
                            "winner": "null"
                        }
                    }
                if not user_can_get_damage(battle, loser_id):
                    data = {
                        "battles_finish": {
                            "winner": winner_id
                        }
                    }
                    await battle.delete()
                    used_battlelogs_count.clear()

                await manager.send_to_room(data, room_name)
    except WebSocketDisconnect:
        manager.remove(websocket, room_name)
