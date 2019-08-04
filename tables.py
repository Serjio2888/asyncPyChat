import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect('postgresql://author@localhost/avt', password='qwerty')
    await conn.execute("""
          CREATE TABLE users (
              id serial PRIMARY KEY,
              username text UNIQUE NOT NULL,
              created_at text
          )
      """)
    await conn.execute("""
            CREATE TABLE chats (
                id serial PRIMARY KEY,
                name text UNIQUE NOT NULL,
                created_at text
           )
       """)
    await conn.execute("""
                CREATE TABLE user_chat (
                    id serial PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    CONSTRAINT "FK_user_id" FOREIGN KEY ("user_id")
                    REFERENCES "users" ("id"),
                    CONSTRAINT "FK_chat_id" FOREIGN KEY ("chat_id")
                    REFERENCES "chats" ("id")
            )
        """)
    await conn.execute("""
                CREATE UNIQUE INDEX "UI_user_chat"
                ON "user_chat"
                USING btree
                ("user_id", "chat_id");
                """)
    await conn.execute("""
            CREATE TABLE messages (
                id serial PRIMARY KEY,
                chat_id integer,
                CONSTRAINT fk_messages_chats FOREIGN KEY (chat_id)  REFERENCES chats (id)
                ON DELETE CASCADE,
                user_id integer,
                CONSTRAINT fk_messages_users FOREIGN KEY (user_id)  REFERENCES users (id)
                ON DELETE CASCADE,
                text text,
                created_at text
            )
        """)
    await conn.close()

asyncio.get_event_loop().run_until_complete(main())