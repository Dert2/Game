from tortoise import Tortoise


async def connect_to_database():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['app_models.models']}
    )