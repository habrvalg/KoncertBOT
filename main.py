from telebot.types import LabeledPrice
from config import token
import telebot
import config
import utils
import json
import base
import os


bot = telebot.TeleBot(token=token)
bot.remove_webhook()
base = base.Database()
base.init_tables()


#  Создание клавиатур
start_user_key = utils.create_keyboard([
	['Мои билеты', 'События']
])
start_admin_key = utils.create_keyboard([
	['Текущие события'],
	['Добавить событие', 'Удалить событие'],
	['Добавить проверяющего', 'Удалить проверяющего']
])
back_key = utils.create_keyboard([
	['Назад']
])
sub_admin_menu = utils.create_keyboard([
	['Проверить билет']
])
confirm_key = utils.create_keyboard([
	['Подтвердить'],
	['Назад']
])


#  Функционал

@bot.message_handler(commands=['start'])
def start_func(message):
	user_id = message.from_user.id
	base.create_user(user_id)
	base.update_user_mode(user_id, 'start')
	if base.check_admin(user_id):
		bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_admin_key)
	elif base.check_sub_admin(user_id):
		bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=sub_admin_menu)
	else:
		bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_user_key)


@bot.message_handler(content_types=['text'])
def main_func(message):
	user_id = message.from_user.id
	msg = message.text

	print(
		f'{message.from_user.username} <{user_id}>: {message.text}'
	)
	user = base.get_user(user_id)

	if base.check_admin(user_id):  # Обработка админов
		if user[1] == 'start':
			if msg == 'Текущие события':
				events = base.get_events()

				count = 1
				text = ''
				for event in events:
					text = f'{text}\n{count}) {event[1]} - {event[2]}'
					count += 1
				text = text.strip()

				if len(events) > 0:
					bot.send_message(
						user_id,
						f'Вот список всех текущих событий:\nВВЕДИТЕ НОМЕР (ЧИСЛО) события, чтобы узнать подробности\n\n{text}'
					)
					bot.send_message(user_id, 'Пришлите номер события, о котором хотите узнать больше:', reply_markup=back_key)

					base.update_user_mode(user_id, 'choice event')
				else:
					bot.send_message(user_id, 'Сейчас нет запущенных событий!')

			elif msg == 'Удалить событие':
				events = base.get_events()

				count = 1
				text = ''
				for event in events:
					text = f'{text}\n{count}) {event[1]} - {event[2]}'
					count += 1
				text = text.strip()

				if len(events) > 0:
					bot.send_message(user_id, f'ВВЕДИТЕ НОМЕР события (ЧИСЛО):\n\n{text}', reply_markup=back_key)
					base.update_user_mode(user_id, 'get num del event')
				else:
					bot.send_message(user_id, 'Сейчас нет запущенных событий!')

			elif msg == 'Добавить событие':
				bot.send_message(user_id, 'Введите название события:', reply_markup=back_key)
				base.update_user_mode(user_id, 'get_new_event_name')

			elif msg == 'Добавить проверяющего':
				bot.send_message(user_id, 'Пришлите Telegram ID пользователя:', reply_markup=back_key)
				base.update_user_mode(user_id, 'get_new_sub_admin_link')

			elif msg == 'Удалить проверяющего':
				bot.send_message(user_id, 'Пришлите Telegram ID пользователя:', reply_markup=back_key)
				base.update_user_mode(user_id, 'get_del_sub_admin_link')

		elif user[1] == 'get_new_sub_admin_link':
			if msg == 'Назад':
				bot.send_message(user_id, 'Выберите действие:', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

			else:
				if msg.isdigit():
					if base.check_user(int(msg)):
						if base.check_admin(int(msg)):
							bot.send_message(
								user_id,
								'Пользователь является администратором, вы не можете его понизить!',
								reply_markup=back_key
							)
						else:
							# Тут добавление пользователя в sub_admins
							bot.send_message(user_id, f'Пользователь {msg} назначен sub-администратором!', reply_markup=start_admin_key)
							base.update_user_mode(user_id, 'start')
							base.add_sub_admin(int(msg))
							bot.send_message(
								int(msg),
								'Вы назначены SUB-админом!\nТеперь вы можете проверять и активировать билеты посетителей!',
								reply_markup=sub_admin_menu
							)
					else:
						bot.send_message(user_id, f'Не удалось найти пользователя с Telegram ID {int(msg)}', reply_markup=back_key)
				else:
					bot.send_message(
						user_id,
						f'Нужно прислать только число!\nНапример: {user_id} (Ваш Telegram ID)',
						reply_markup=back_key
					)

		elif user[1] == 'get_del_sub_admin_link':
			if msg == 'Назад':
				bot.send_message(user_id, 'Выберите действие:', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

			else:
				if msg.isdigit():
					if base.check_user(int(msg)):
						if base.check_admin(int(msg)):
							bot.send_message(
								user_id,
								'Пользователь является администратором, вы не можете его понизить!',
								reply_markup=back_key
							)
						else:
							# Тут удаление пользователя из sub_admins
							base.del_sub_admin(int(msg))
							bot.send_message(
								int(msg),
								'Вы были сняты с должности SUB-админа!\nТеперь вы не можете проверять и активировать билеты посетителей!',
								reply_markup=start_user_key
							)
					else:
						bot.send_message(
							user_id,
							f'Не удалось найти пользователя с Telegram ID {int(msg)}',
							reply_markup=back_key
						)
				else:
					bot.send_message(
						user_id,
						f'Нужно прислать только число!\nНапример: {user_id} (Ваш Telegram ID)',
						reply_markup=back_key
					)

		elif user[1] == 'get_new_event_name':
			if msg == 'Назад':
				bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

			else:
				base.cur.execute(f'insert into temp(tg_id, name, value) values({user_id}, "new_event_name", "{msg}")')
				bot.send_message(user_id, 'Укажите дату мероприятия:', reply_markup=back_key)
				base.update_user_mode(user_id, 'get_event_date')

		elif user[1] == 'get_event_date':
			if msg == 'Назад':
				base.clear_temp(user_id)
				bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

			else:
				base.cur.execute(f'insert into temp(tg_id, name, value) values({user_id}, "new_event_date", "{msg}")')
				bot.send_message(user_id, 'Укажите кол-во билетов на мероприятие:', reply_markup=back_key)
				base.update_user_mode(user_id, 'get_new_event_count_tic')

		elif user[1] == 'get_new_event_count_tic':
			if msg == 'Назад':
				base.clear_temp(user_id)
				bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

			else:
				if msg.isdigit():
					base.cur.execute(f'insert into temp(tg_id, name, value) values({user_id}, "new_event_count_tic", "{int(msg)}")')
					bot.send_message(user_id, 'Укажите цену за билет в рублях:', reply_markup=back_key)
					base.update_user_mode(user_id, 'get_new_event_price')
				else:
					bot.send_message(user_id, 'Введите кол-во билетов (число):')

		elif user[1] == 'get_new_event_price':
			if msg == 'Назад':
				base.clear_temp(user_id)
				bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

			else:
				if msg.isdigit():
					base.cur.execute(f'insert into temp(tg_id, name, value) values({user_id}, "new_event_price", "{msg}")')
					bot.send_message(user_id, 'Добавьте описание к событию:', reply_markup=back_key)
					base.update_user_mode(user_id, 'get_new_event_comment')
				else:
					bot.send_message(user_id, 'Введите цену билета (число):')

		elif user[1] == 'get_new_event_comment':
			if msg == 'Назад':
				base.clear_temp(user_id)
				bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

			else:
				base.cur.execute(f'insert into temp(tg_id, name, value) values({user_id}, "new_event_comment", "{msg}")')
				bot.send_message(user_id, 'Пришлите фото для обложки события:', reply_markup=back_key)
				base.update_user_mode(user_id, 'get_new_event_photo')

		elif user[1] == 'get_new_event_photo':

			if message.text == 'Назад':
				base.clear_temp(user_id)
				bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

		elif user[1] == 'choice event':

			if msg == 'Назад':
				bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

			else:
				events = base.get_events()

				if msg.isdigit():
					if len(events) > int(msg)-1 >= 0:

						event = base.get_event_by_name(events[int(msg)-1][1])
						bought = base.get_tickets_count(event[0])

						answer = f'{event[1]} - {event[2]}\n\nЦена билета: {int(event[3])}₽\nКуплено: {bought} билетов'\
															f' на сумму {bought*event[3]}₽\n\n{event[6]}'

						with open(event[5], 'rb') as file:
							photo = file.read()

						bot.send_photo(user_id, photo, caption=answer, reply_markup=start_admin_key)
						base.update_user_mode(user_id, 'start')

					else:
						bot.send_message(user_id, 'Нет события с таким номером!')
				else:
					bot.send_message(user_id, 'Введите только число (номер события как он указан)!')

		elif user[1] == 'get num del event':
			if msg == 'Назад':
				bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_admin_key)
				base.update_user_mode(user_id, 'start')

			else:
				events = base.get_events()

				if msg.isdigit():
					if len(events) > int(msg) - 1 >= 0:
						event_name = events[int(msg) - 1][1]

						base.delete_event_by_name(event_name)
						bot.send_message(user_id, f'Событие {event_name} успешно удалено!', reply_markup=start_admin_key)
						base.update_user_mode(user_id, 'start')

	elif base.check_sub_admin(user_id):
		# Обработка sub-админов
		if user[1] == 'start':
			if msg == 'Проверить билет':
				bot.send_message(user_id, 'Отсканируйте билет (QR код) и введите данные из него:', reply_markup=back_key)
				base.update_user_mode(user_id, 'get_qr_data')

		elif user[1] == 'get_qr_data':
			if msg == 'Назад':
				bot.send_message(user_id, 'Выберите действие:', reply_markup=sub_admin_menu)
				base.update_user_mode(user_id, 'start')

			elif '_' in msg:
				data = msg.split('_')
				user_data = data[0]
				event_data = data[1]

				if event_data.isdigit() and user_data.isdigit():
					if base.check_user_ticket(user_data, event_data):

						event = base.get_event_by_id(int(event_data))

						with open(event[5], 'rb') as file:
							bot.send_photo(
								user_id,
								file.read(),
								caption='Проверьте билет и подтвердите его.\nПосле подтверждения билет нельзя будет использовать повторно!',
								reply_markup=confirm_key
							)
							base.cur.execute(
								f'insert into temp(tg_id, name, value) values({user_id}, "confirm event ticket event_id", "{event_data}")'
							)
							base.cur.execute(
								f'insert into temp(tg_id, name, value) values({user_id}, "confirm event ticket user_id", "{user_data}")'
							)
							base.update_user_mode(user_id, 'confirm_ticket')

					else:
						bot.send_message(user_id, 'Билет не найден либо уже использован!', reply_markup=back_key)
				else:
					bot.send_message(user_id, 'Код не соответствует параметрам!', reply_markup=back_key)
			else:
				bot.send_message(user_id, 'Код не соответствует параметрам!', reply_markup=back_key)

		elif user[1] == 'confirm_ticket':
			if msg == 'Назад':
				bot.send_message(user_id, 'Выберите действие:', reply_markup=sub_admin_menu)
				base.clear_temp(user_id)
				base.update_user_mode(user_id, 'start')

			elif msg == 'Подтвердить':
				user_temp = base.get_user_temp(user_id)
				event_data = int(user_temp['confirm event ticket event_id'])
				user_data = int(user_temp['confirm event ticket user_id'])
				event = base.get_event_by_id(event_data)

				base.mark_ticket_as_used(user_data, event_data)
				bot.send_message(
					user_id,
					'Билет пользователя был активирован!\nПовторно его использовать нельзя!',
					reply_markup=sub_admin_menu
				)
				base.update_user_mode(user_id, 'start')

				with open(event[5], 'rb') as file:
					bot.send_photo(
						user_data,
						file.read(),
						caption=f'Ваш билет на событие "{event[1]}" активирован!\nЖелаем вам хорошо провести время!'
					)

				base.clear_temp(user_id)

	else:  # Обработка простых пользователей
		if user[1] == 'start':
			if msg == 'Мои билеты':
				user_tickets = base.get_user_tickets(user_id)

				if len(user_tickets) > 0:
					count = 1
					answer = 'ВВЕДИТЕ НОМЕР билета (ЧИСЛО) чтобы узнать подробности:\n\n'
					for ticket in user_tickets:
						answer += f'{count}) {ticket[1]}\n'
						count += 1

					bot.send_message(user_id, answer, reply_markup=back_key)
					base.update_user_mode(user_id, 'choice_my_ticket')

				else:
					bot.send_message(user_id, 'У вас нет купленных билетов!')

			elif msg == 'События':
				events = base.get_events()
				msg_text = f'Вот список всех текущих событий:\nВВЕДИТЕ НОМЕР (ЧИСЛО) события, чтобы узнать подробности\n\n'

				count = 1
				for event in events:
					msg_text += f'{count}) {event[1]}\n'
					count += 1

				bot.send_message(user_id, msg_text, reply_markup=back_key)
				base.update_user_mode(user_id, 'get_event_number')

		elif user[1] == 'choice_my_ticket':
			if msg == 'Назад':
				bot.send_message(user_id, f'Привет, {message.from_user.first_name}!', reply_markup=start_user_key)
				base.update_user_mode(user_id, 'start')

			else:
				if msg.isdigit():
					user_tickets = base.get_user_tickets(user_id)
					if 0 < int(msg) <= len(user_tickets):
						ticket = user_tickets[int(msg) - 1]
						msg_text = f'Ваш билет на событие "{ticket[1]}" {ticket[2]}'
						qr_path = [
							x for x in base.cur.execute(
								f'select qr_path from tickets where user_id={user_id} and event_id={ticket[0]}'
							)
						][0][0]

						with open(qr_path, 'rb') as file:
							bot.send_photo(user_id, file.read(), caption=msg_text)
						bot.send_message(user_id, 'Выберите действие:', reply_markup=start_user_key)
						base.update_user_mode(user_id, 'start')
					else:
						bot.send_message(user_id, 'Выберите номер из ранне присланного сообщения!')
				else:
					bot.send_message(user_id, 'Необходимо прислать только число!')

		elif user[1] == 'get_event_number':
			if msg == 'Назад':
				bot.send_message(user_id, 'Выберите действие:', reply_markup=start_user_key)
				base.update_user_mode(user_id, 'start')

			else:
				if msg.isdigit():
					events = base.get_events()
					if 0 < int(msg) <= len(events):
						event = base.get_event_by_id(events[int(msg) - 1][0])
						msg_text = f'{event[1]} {event[2]}\nЦена билета - {int(event[3])}₽\nОписание: {event[6]}'

						user_payed_tickets = [x[0] for x in base.cur.execute(f'select event_id from tickets where user_id={user_id}')]

						if event[0] in user_payed_tickets:
							with open(event[5], 'rb') as file:
								bot.send_photo(
									user_id,
									file.read(),
									caption=msg_text,
									reply_markup=utils.create_keyboard([['Назад']])
								)
						else:
							with open(event[5], 'rb') as file:
								bot.send_photo(
									user_id,
									file.read(),
									caption=msg_text,
									reply_markup=utils.create_keyboard([['Купить билет', 'Назад']])
								)
						base.update_user_mode(user_id, f'info_event_{event[0]}')

					else:
						bot.send_message(user_id, 'Нет события с таким номером!')
				else:
					bot.send_message(user_id, 'Пришлите только номер события!')

		elif user[1].startswith('info_event_') and user[1].replace('info_event_', '', 1).isdigit():
			if msg == 'Назад':
				bot.send_message(user_id, 'Выберите действие:', reply_markup=start_user_key)
				base.update_user_mode(user_id, 'start')

			elif msg == 'Купить билет':  # тут нужно реализовать оплату биллета
				event_id = base.get_event_by_id(int(user[1].replace('info_event_', '', 1)))[0]

				if not(os.path.exists(f'qrs/{user_id}_{event_id}.jpg')):
					event = base.get_event_by_id(event_id)

					# Выставление счёта в чате
					payload = '{' + f'"user_id": {user_id}, "event_id": {event_id}' + '}'
					bot.send_invoice(
						chat_id=user_id,
						title=f'Билет на событие "{event[1]}"',
						description=event[6],
						invoice_payload=payload,
						provider_token=config.sber_token,
						currency="RUB",
						start_parameter='test',
						prices=[LabeledPrice(label='labeled_price', amount=int(event[3]*100))]
					)

				else:
					bot.send_message(user_id, 'У вас уже куплен данный билет!')


@bot.pre_checkout_query_handler(lambda query: True)
def pre_checkout(pre_checkout_query: telebot.types.PreCheckoutQuery):
	event_id = json.loads(pre_checkout_query.invoice_payload)['event_id']
	if base.check_tickets(event_id):
		bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
	else:
		bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False)


@bot.message_handler(content_types=['successful_payment'])
def get_payment(message):
	payment_payload = json.loads(message.successful_payment.invoice_payload)
	event = base.get_event_by_id(payment_payload['event_id'])
	event_name = event[1]
	qr_data = utils.get_qr_code(base, str(message.from_user.id), str(payment_payload['event_id']))
	caption = f'{message.from_user.first_name}, поздравляем!\nВы успешно приобрели билет на событие {event_name}!'
	with open(event[5], 'rb') as file:
		bot.send_photo(message.from_user.id, file.read(), caption=caption, reply_markup=start_user_key)
	bot.send_photo(message.from_user.id, qr_data, caption='Вот ваш билет!')
	base.update_user_mode(message.from_user.id, 'start')
	print(f'Пользователь <{message.from_user.first_name}> КУПИЛ БИЛЕТ!')


@bot.message_handler(content_types=['photo'])
def get_image(message):
	user_id = message.from_user.id
	user = base.get_user(user_id)

	if base.check_admin(user_id):
		if user[1] == 'get_new_event_photo':
			file_name = bot.get_file(message.photo[-1].file_id).file_path
			photo = bot.download_file(file_name)

			cur_file_name = f"{os.getcwd()}\\{file_name}".replace('/', '\\')

			with open(cur_file_name, 'wb') as file:
				file.write(photo)

			new_event_data = base.get_user_temp(user_id)

			base.create_event(
				new_event_data['new_event_name'],
				new_event_data['new_event_date'],
				new_event_data['new_event_price'],
				new_event_data['new_event_count_tic'],
				cur_file_name,
				new_event_data['new_event_comment']
			)

			base.clear_temp(user_id)
			bot.send_message(user_id, 'Событие создано!')

			with open(cur_file_name, 'rb') as file:
				event = base.get_event_by_name(new_event_data['new_event_name'])
				bought = base.get_tickets_count(event[0])

				answer = f'{event[1]} - {event[2]}\n\nЦена билета: {int(event[3])}₽\nКуплено: {bought} билетов на '\
													f'сумму {bought * event[3]}₽\n\n{event[6]}'
				bot.send_photo(user_id, file.read(), caption=answer)

			bot.send_message(user_id, f'Выберите действие:', reply_markup=start_admin_key)
			base.update_user_mode(user_id, 'start')


if __name__ == '__main__':
	bot.infinity_polling(timeout=10, long_polling_timeout=5)
