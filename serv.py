from aiohttp import web
import json
import asyncpg
from datetime import datetime


class ChatWorker():
    def __init__(self):
        self.conn = None

    async def connecting(self):
        self.conn = await asyncpg.connect('postgresql://author@localhost/avt', password='qwerty')

    async def get_info_about(self, name, chat=False, user=False):
        """
            Проверяет существует ли пользователь или чат,
            в зависимости от того, какой аргумент (chat/user) передан со значением True
        """
        if chat:
            table = 'chats'
            field = 'name'
        elif user:
            table = 'users'
            field = 'username'
        return await self.conn.fetchrow(
            'SELECT id FROM '+table+' WHERE '+field+' = $1', name)

    async def new_user(self, name):
        await self.conn.execute('''
                    INSERT INTO users(username, created_at) VALUES($1, $2)
                    ''', name, str(datetime.now()))
        return await self.get_info_about(name, user=True)

    async def add_user(self, request):
        if not self.conn:
            await self.connecting()
        user = await request.json()
        name = user.get('username')
        if name:
            if not await self.get_info_about(name, user=True): #проверяем, нет ли такого юзера
                id = await CW.new_user(name)
                return web.Response(body=json.dumps({'id':id[0]}), status=201)
            else:
                return web.Response(text='Username is already registered!', status=409, reason=None)
        else:
            return web.Response(text='Incorrect Request!', status=405, reason=None)

    async def new_chat(self, name, users):
        await self.conn.execute('''
                    INSERT INTO chats(name, created_at) VALUES($1, $2)
                    ''', name, str(datetime.now()))
        chat = await self.get_info_about(name, chat=True)
        async with self.conn.transaction():
            for i in users:
                await self.conn.execute("INSERT INTO user_chat(user_id, chat_id) \
                                         VALUES($1, $2)", int(i), chat[0])
        return chat[0]

    async def add_chat(self, request):
        if not self.conn:
            await self.connecting()
        chat = await request.json()
        name = chat.get('name')
        users = chat.get('users')
        if name and users:
            if not await self.get_info_about(name, chat=True): #проверяем, нет ли такого чата
                id = await CW.new_chat(name, users)
                return web.Response(body=json.dumps({'id':id}), status=201)
            else:
                return web.Response(text='This chat is already registered!', status=409, reason=None)
        else:
            return web.Response(text='Incorrect Request!', status=405, reason=None)

    async def select_chat_users(self, chat_id):
        rows = await self.conn.fetch('SELECT * FROM user_chat WHERE chat_id = $1', chat_id)
        return list(i[1] for i in rows) #список id юзеров, состоящих в чате

    async def select_user_chats_info(self, user_id):
        rows = await self.conn.fetch('SELECT * FROM user_chat WHERE user_id = $1', int(user_id))
        chats = list(i[2] for i in rows)
        info = dict()
        for k, i in enumerate(chats):
            chat = await self.conn.fetchrow('SELECT * FROM chats WHERE id = $1', int(i))
            name = chat['name']
            users = await self.select_chat_users(chat['id'])
            created_at = chat['created_at']
            info[k] = {'name':name, 'users':users, 'created_at':created_at}
        return info

    async def new_msg(self, chat, author, text):
        now = str(datetime.now())
        await self.conn.execute('''
                    INSERT INTO messages(chat_id, user_id, text, created_at) VALUES($1, $2, $3, $4)
                    ''', int(chat), int(author), text, now)
        row = await self.conn.fetchrow('SELECT id FROM messages \
                                        WHERE user_id = $1 AND created_at = $2', int(author), now)
        return row[0]

    async def send_msg(self, request):
        if not self.conn:
            await self.connecting()
        msg = await request.json()
        chat = msg.get('chat')
        author = msg.get('author')
        text = msg.get('text')
        if chat and author and text:
            if int(author) in await self.select_chat_users(int(chat)): #проверка на принадлежность юзера чату
                id = await CW.new_msg(chat, author, text)
                return web.Response(body=json.dumps({'id':id}), status=201)
            else:
                return web.Response(text='This user do not belong to this chat!', 
                                    status=403, reason=None)
        else:
            return web.Response(text='Incorrect Request!', status=405, reason=None)

    async def get_chats(self, request):
        if not self.conn:
            await self.connecting()
        user = (await request.json()).get('user')
        if user:
            info = await self.select_user_chats_info(user)
            return web.Response(body=json.dumps(info), status=200)
        else:
            return web.Response(text='Incorrect Request!', status=405, reason=None)

    async def get_chat_messages(self, request):
        if not self.conn:
            await self.connecting()
        chat_id = (await request.json()).get('chat')
        if chat_id:
            rows = await self.conn.fetch('SELECT * FROM messages WHERE chat_id = $1', int(chat_id))
            info = dict()
            for k, i in enumerate(rows):
                user_id = i[2]
                text = i[3]
                created_at = i[4]
                info[k] = {'user_id':user_id, 'text':text, 'created_at':created_at}
            return web.Response(body=json.dumps(info), status=200)
        else:
            return web.Response(text='Incorrect Request!', status=405, reason=None)


CW = ChatWorker()
app = web.Application()
app.add_routes([web.post('/users/add', CW.add_user)])
app.add_routes([web.post('/chats/add', CW.add_chat)])
app.add_routes([web.post('/messages/add', CW.send_msg)])
app.add_routes([web.post('/chats/get', CW.get_chats)])
app.add_routes([web.post('/messages/get', CW.get_chat_messages)])
web.run_app(app, port=9000)


