from pydantic_models import BattleMoveModel
import random


# choice --> 0 - rock, 1 - paper, 2 - scissors
def check_winner_and_loser(
        first_user_move: BattleMoveModel,
        second_user_move: BattleMoveModel
):
    if first_user_move.choice == second_user_move.choice:
        return None, None
    elif first_user_move.choice == 0:
        if second_user_move.choice == 1:
            return first_user_move.userId, second_user_move.userId
        else:
            return second_user_move.userId, first_user_move.userId
    elif first_user_move.choice == 2:
        if second_user_move.choice == 0:
            return first_user_move.userId, second_user_move.userId
        else:
            return second_user_move.userId, first_user_move.userId
    elif first_user_move.choice == 1:
        if second_user_move.choice == 2:
            return first_user_move.userId, second_user_move.userId
        else:
            return second_user_move.userId, first_user_move.userId


async def damage_loser(battle, loser_id: int) -> None:
    if battle.offerUserId == loser_id and battle.healthOfferUserId > 0:
        battle.healthOfferUserId -= random.randint(10, 20)
        await battle.save()
    elif battle.acceptUserId == loser_id and battle.healthAcceptUserId > 0:
        battle.healthAcceptUserId -= random.randint(10, 20)
        await battle.save()


def user_can_get_damage(battle, loser_id: int) -> bool:
    if loser_id is None:
        return True
    elif battle.offerUserId == loser_id and battle.healthOfferUserId > 0:
        return True
    elif battle.acceptUserId == loser_id and battle.healthAcceptUserId > 0:
        return True
    else:
        return False
