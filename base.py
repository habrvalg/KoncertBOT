import sqlite3
import os


class Database:
	def __init__(self):
		if not os.path.exists('data.db'):
			with open('data.db', 'w') as file:
				print(f"file {file.name} created!")
		self.conn = sqlite3.connect('data.db', check_same_thread=False)
		self.cur = self.conn.cursor()

	def init_tables(self):
		tables = [
			'users(tg_id integer, mode varchar(100))',
			'events(id integer primary key, name varchar(300), date text, price real, '
			'ticket_count integer, photo text, comment text)',
			'tickets(id integer primary key, user_id integer, event_id integer, is_used byte, qr_path text)',
			'admins(tg_id integer)',
			'sub_admins(tg_id integer)',
			'temp(tg_id integer, name text, value text)'
		]
		for table_template in tables:
			self.cur.execute(f"create table if not exists {table_template}")
		self.conn.commit()

	def add_sub_admin(self, tg_id):
		self.cur.execute(f'insert into sub_admins(tg_id) values({tg_id})')
		self.conn.commit()

	def del_sub_admin(self, tg_id):
		self.cur.execute(f'delete from sub_admins where tg_id={tg_id}')
		self.conn.commit()

	def create_user(self, tg_id):
		if len([x for x in self.cur.execute(f'select * from users where tg_id={tg_id}')]) < 1:
			self.cur.execute(f'insert into users(tg_id, mode) values({tg_id}, "start")')
		self.conn.commit()

	def update_user_mode(self, tg_id, mode):
		self.cur.execute(f'update users set mode="{mode}" where tg_id={tg_id}')
		self.conn.commit()

	def check_admin(self, tg_id):
		return len([x for x in self.cur.execute(f'select * from admins where tg_id={tg_id}')]) > 0

	def check_sub_admin(self, tg_id):
		return len([x for x in self.cur.execute(f'select * from sub_admins where tg_id={tg_id}')]) > 0

	def get_user(self, tg_id):
		user = [x for x in self.cur.execute(f'select * from users where tg_id={tg_id}')]
		if len(user) > 0:
			return user[0]
		self.create_user(tg_id)
		return [x for x in self.cur.execute(f'select * from users where tg_id={tg_id}')][0]

	def check_user(self, tg_id):
		return len([x for x in self.cur.execute(f'select * from users where tg_id={tg_id}')]) > 0

	def get_events(self):
		return [x for x in self.cur.execute('select * from events')]

	def clear_temp(self, tg_id):
		self.cur.execute(f'delete from temp where tg_id={tg_id}')
		self.conn.commit()

	def get_user_temp(self, tg_id):
		out = {}
		for el in [{x[0]: x[1]} for x in self.cur.execute(f'select name, value from temp where tg_id={tg_id}')]:
			out.update(el)
		return out

	def create_event(self, name, date, price, count_tic, photo, comment):
		self.cur.execute(
			'insert into events(name, date, price, ticket_count, photo, comment)'
			f'values("{name}", "{date}", {price}, {count_tic}, "{photo}", "{comment}")'
		)
		self.conn.commit()

	def get_event_by_name(self, name):
		event = [x for x in self.cur.execute(f'select * from events where name="{name}"')]
		if len(event) > 0:
			return event[0]
		else:
			return None

	def get_event_by_id(self, t_id):
		event = [x for x in self.cur.execute(f'select * from events where id={t_id}')]
		if len(event) > 0:
			return event[0]
		else:
			return None

	def delete_event_by_name(self, name):
		event_id = self.get_event_by_name(name)[0]

		# Удаляем QR коды билетов
		for path in [x[0] for x in self.cur.execute(f'select qr_path from tickets where event_id={event_id}')]:
			os.remove(path)

		# Удаляем билеты из бд
		self.cur.execute(f'delete from tickets where event_id={event_id}')

		# Удаляем обложку ивента
		event_photo_path = [x for x in self.cur.execute(f'select photo from events where name="{name}"')][0][0]
		os.remove(event_photo_path)
		self.cur.execute(f'delete from events where name="{name}"')
		self.conn.commit()

	def get_tickets_count(self, e_id):
		return len([x for x in self.cur.execute(f'select * from tickets where event_id={e_id}')])

	def get_user_tickets(self, tg_id):
		user_tickets_ids = [x for x in self.cur.execute(f'select * from tickets where user_id={tg_id}')]
		user_tickets = []

		for ticket in user_tickets_ids:
			user_tickets.append(self.get_event_by_id(ticket[2]))

		return user_tickets

	def add_ticket(self, user_id, event_id, qr_path):
		self.cur.execute(
			'insert into tickets(user_id, event_id, is_used, qr_path) '
			f'values({user_id}, {event_id}, 0, "{qr_path}")'
		)
		self.conn.commit()

	def check_tickets(self, event_id):
		max_count = [x for x in self.cur.execute(f'select ticket_count from events where id={event_id}')][0][0]
		current_count = len([x for x in self.cur.execute(f'select * from tickets where event_id={event_id}')])
		return current_count < max_count

	def check_user_ticket(self, user_id, event_id):
		return len(
			[x for x in self.cur.execute(f'select * from tickets where user_id={user_id} and event_id={event_id} and is_used=0')]
		) > 0

	def mark_ticket_as_used(self, user_id, event_id):
		self.cur.execute(f'update tickets set is_used=1 where user_id={user_id} and event_id={event_id}')


if __name__ == '__main__':
	Database().init_tables()
