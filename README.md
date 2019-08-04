# asyncPyChat
pure chat working on aiohttp

Асинхронный чат работает на Python aiohttp + postgresql

Схема БД:
![text](https://c.radikal.ru/c30/1908/88/4dda7657dfb7.jpg)

 Что нужно для работы (на ubuntu 16.04):
  - sudo apt install python3.7 
  - библиотеки: asyncio + asyncpg + json (установка библиотек через pip install libname)
  - postgresql. Подробная инструкция по установке и настройке БД: https://losst.ru/ustanovka-postgresql-ubuntu-16-04
  - создать пользователя author (использовать пароль 'qwerty') и БД avt (можно использовать другие названия, но тогда надо будет поменять 5-ю строку в tables.py и 12-ю строку в serv.py
  - после чего запустить скрипт tables.py - он создаст таблицы в нашей БД
  - и запустить serv.py - это наш сервер
  
  Теперь можно отправлять команды через curl. Сервер работает на порту 9000.
  
 Особенности:
  - в таблице chats нет поля users. Я посчитал, что это избыточно , т.к. получить юзеров из чата можно через таблицу user_chat
