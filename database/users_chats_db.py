import re
import motor.motor_asyncio
import logging
from info import DATABASE_NAME, DATABASE_URI

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    async def ping_server(self):
        try:
            await self.db.command('ping')
            logging.info("Database ping successful - Connection is alive.")
        except Exception as e:
            logging.error(f"Database ping failed: {e}")

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            is_banned = False,
            ban_reason = "",
            has_password = False
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def ban_user(self, user_id, reason):
        await self.col.update_one({'id': int(user_id)}, {'$set': {'is_banned': True, 'ban_reason': reason}})

    async def unban_user(self, user_id):
        await self.col.update_one({'id': int(user_id)}, {'$set': {'is_banned': False, 'ban_reason': ''}})

    async def is_user_banned(self, user_id):
        user = await self.col.find_one({'id': int(user_id)})
        if user:
            return user.get('is_banned', False), user.get('ban_reason', '')
        return False, ''

    async def get_password(self, id):
        user = await self.col.find_one({'id':int(id)})
        if user:
            return user.get('has_password', False)
        return False

    async def set_password(self, id, has_password):
        await self.col.update_one({'id': int(id)}, {'$set': {'has_password': has_password}})

    async def save_file_mapping(self, primary_id, backup_id):
        await self.db.files.update_one(
            {'primary_id': int(primary_id)},
            {'$set': {'backup_id': int(backup_id)}},
            upsert=True
        )

    async def get_backup_id(self, primary_id):
        file_data = await self.db.files.find_one({'primary_id': int(primary_id)})
        if file_data:
            return file_data.get('backup_id')
        return None


db = Database(DATABASE_URI, DATABASE_NAME)
