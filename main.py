import telebot
from telebot import types
import random
bot = telebot.TeleBot('*', parse_mode=None)


class Creature:
    def __init__(self, name, simbol, health, damage, gold):
        self._name = name
        self._simbol = simbol
        self._health = health
        self._damage = damage
        self._gold = gold
        self._fullHealth = health

    @property  # аннотация геттера
    def name(self): return self._name

    @property  # аннотация геттера
    def simbol(self): return self._simbol

    @property  # аннотация геттера
    def health(self): return self._health

    @property  # аннотация геттера
    def damage(self): return self._damage

    @property  # аннотация геттера
    def gold(self): return self._gold

    def reduceHealth(self, damage):
        self._health = self._health - damage
        return self._health

    def isDead(self):
        if self._health <= 0:
            return True

    def addGold(self, gold):
        self._gold = self._gold + gold
        return self._gold

    def nullGold(self):
        self._gold = 0
        return self._gold

    def fullHealth(self):
        self._health = self._fullHealth


class Player(Creature):
    __level = 1

    def levelUp(self):
        self.__level = self.__level + 1
        self._damage = self._damage + 1

    def levelDowm(self):
        self.__level = 1
        self._damage = 1

    def hasWon(self):
        if self.__level == 3:
            return True

    @property
    def level(self): return self.__level


class Monster(Creature):
    DRAGON = Creature('Дракон', 'D', 20, 4, 100)
    ORC = Creature('Орк', 'o', 4, 2, 25)
    SLIME = Creature('Слизняк', 's', 1, 1, 10)
    Monsters = [DRAGON, ORC, SLIME]


def randomMonsters():
    randM = Monster.Monsters[random.randint(0, 2)]
    return randM


def attackPlayer(message, m, p):
    if (m.isDead() == True):
        return
    p.reduceHealth(m.damage)
    bot.send_message(message.chat.id, f'{m.name} наносит вам {m.damage} единиц урона.')


def attackMonster(message, m, p):
    if p.isDead() == True:
        return
    print('я бью ' + m.name)
    bot.send_message(message.chat.id, f'Вы бьете {m.name} и наносите {p.damage} единиц урона.')
    m.reduceHealth(p.damage)
    if m.health > 0:
        bot.send_message(message.chat.id, f'Здоровье {m.name} = {m.health}')
    if (m.isDead() == True):
        bot.send_message(message.chat.id, f'Вы убили {m.name}.')
        p.levelUp()
        bot.send_message(message.chat.id, f'Ваш уровень {p.level}.')
        bot.send_message(message.chat.id, f'Вы нашли {m.gold} золотых.')
        p.addGold(m.gold)



#def playerisDead(message):
#    bot.send_message(message.chat.id, f'Вы достигли {p.level} '
#        f'уровня и унесли с собой в могилу {p.gold} золотых.')
#    bot.stop_polling()



def choiceBattle(message, monster, p):
    keyboard_next = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_next.row('Продолжим')
    keyboard_dead = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_dead.row('Естественно')
    print('Кого я встретил на самом деле ' + monster.name)
    if (p.isDead() != True and monster.isDead() != True):
        msg = message.text.lower()
        if msg == 'бежать':
            if (random.randint(0, 1) == 1):
                bot.send_message(message.chat.id, 'Вы сбежали')
                print('ты сбежал от ' + monster.name)
                monster.fullHealth()
                send = bot.send_message(message.chat.id, 'Продолжим?', reply_markup=keyboard_next)
                bot.register_next_step_handler(send, battle, p)
                return
            else:
                bot.send_message(message.chat.id, 'Вам не удалось сбежать')
                attackPlayer(message, monster, p)
                if p.isDead() == True:
                    bot.send_message(message.chat.id, 'ТЫ МЕРТВЕТС!!!')
                    bot.send_message(message.chat.id, f'Вы достигли {p.level} '
                            f'уровня и унесли с собой в могилу {p.gold} золотых.')
                    send = bot.send_message(message.chat.id, 'Сыграем еще раз?', reply_markup=keyboard_dead)
                    p.fullHealth()
                    monster.fullHealth()
                    p.levelDowm()
                    p.nullGold()
                    bot.register_next_step_handler(send, battle, p)
                    #bot.stop_polling()
                    return
                send = bot.send_message(message.chat.id, 'Бежать или драться?')
                bot.register_next_step_handler(send, choiceBattle, monster, p)
        if msg == 'драться':
            attackMonster(message, monster, p)
            attackPlayer(message, monster, p)
            if p.isDead() == True:
                bot.send_message(message.chat.id, 'ТЫ МЕРТВЕТС!!!')
                bot.send_message(message.chat.id, f'Вы достигли {p.level} '
                        f'уровня и унесли с собой в могилу {p.gold} золотых.')
                send = bot.send_message(message.chat.id, 'Сыграем еще раз?', reply_markup=keyboard_dead)
                p.fullHealth()
                monster.fullHealth()
                p.levelDowm()
                p.nullGold()
                bot.register_next_step_handler(send, battle, p)
                #bot.stop_polling()
                #bot.register_next_step_handler(message, playerisDead)
                return
            if monster.isDead():
                monster.fullHealth()
                send = bot.send_message(message.chat.id, 'Продолжим?', reply_markup=keyboard_next)
                bot.register_next_step_handler(send, battle, p)
                return
            send = bot.send_message(message.chat.id, 'Бежать или драться?')
            bot.register_next_step_handler(send, choiceBattle, monster, p)
    else:
        bot.send_message(message.chat.id, 'ТЫ МЕРТВЕТС!!!')
        bot.send_message(message.chat.id, f'Вы достигли {p.level} '
                f'уровня и унесли с собой в могилу {p.gold} золотых.')
        send = bot.send_message(message.chat.id, 'Сыграем еще раз?', reply_markup=keyboard_dead)
        p.fullHealth()
        monster.fullHealth()
        p.levelDowm()
        p.nullGold()
        bot.register_next_step_handler(send, battle, p)
        #bot.stop_polling()

@bot.message_handler(commands=['start'])
def start(m, res=False):
    keyboard_start = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_start.row('Погнали')
    print(m.chat.id)
    p = Player(f'{str(m.chat.id)}', '@', 10, 1, 0)
    p.fullHealth()
    p.levelDowm()
    p.nullGold()
    bot.send_message(m.chat.id, f'Привет {m.from_user.first_name}.')
    bot.send_message(m.chat.id, 'ПРАВИЛА ИГРЫ! Чтобы начать играть '
                                'пишите "играть" без кавычек')
    bot.send_message(m.chat.id, 'Когда вас спросят БЕЖАТЬ ИЛИ ДРАТЬСЯ? '
                                'НУЖНО НАПЕЧАТАТЬ БЕЖАТЬ ИЛИ ДРАТЬСЯ соответсвенно,'
                                'если вы напишите что то другое, то ваша игра закончится, '
                                'потому что пока нет обработки ввода')
    bot.send_message(m.chat.id, 'Если вы все таки ошиблись или вам стало интересно, '
                                'что будет если я буду играть не по правилам, '
                                'то напишите /start чтобы запустить бота заново')
    bot.send_message(m.chat.id, 'Цель игры - получить 20 уровень')
    send = bot.send_message(m.chat.id, 'Готовы?', reply_markup=keyboard_start)
    bot.register_next_step_handler(send, battle, p)

@bot.message_handler(func=lambda message: message.text.lower() == 'играть')
def battle(message, p):
    keyboard_win = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_win.row('Да')
    keyboard_choice = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_choice.row('Бежать', 'Драться')
    if (p.isDead() != True and p.hasWon() != True):
        #bot.send_message(message.chat.id, 'Нет пути назад')
        monster = randomMonsters()
        bot.send_message(message.chat.id, f'Вы встретили {monster.name}')
                #reply_markup=telebot.types.ReplyKeyboardRemove()) # Удаляем предыдущую кнопку
        print('Вы встретили ' + monster.name + ' (' + monster.simbol + ')')
        bot.send_message(message.chat.id, f'Здоровье {monster.name} {monster.health}')
        bot.send_message(message.chat.id, f'Ваше здоровье {p.health} .')
        send = bot.send_message(message.chat.id, 'Бежать или драться?', reply_markup=keyboard_choice)
        bot.register_next_step_handler(send, choiceBattle, monster, p)
    elif p.hasWon() == True:
        bot.send_message(message.chat.id, f'ВЫ ПОБЕДИЛЕ и заработали '
                                          f'{p.gold} монет.')
        with open('winners.txt', 'r', encoding='utf-8') as f:
            for i in f:
                data = i.split()
                with open('winners_temp.txt', 'a', encoding='utf-8') as f_over:
                    f_over.write(f'{data[0]} {data[1]} {data[2]} {data[3]} {data[4]}\n')
        with open('winners.txt', 'w+', encoding='utf-8') as f:
            f.seek(0)
        count_user = 0
        with open('winners_temp.txt', 'r', encoding='utf-8') as f_read:
            for k in f_read:
                data = k.split()
                if data[1] == message.from_user.first_name and int(data[4]) < p.gold:
                    count_user = count_user + 1
                    data[4] = str(p.gold)
                    with open('winners.txt', 'a', encoding='utf-8') as f_final:
                        f_final.write(f'{data[0]} {data[1]} {data[2]} {data[3]} {data[4]}\n')
                elif data[1] == message.from_user.first_name and int(data[4]) >= p.gold:
                    with open('winners.txt', 'a', encoding='utf-8') as f_final:
                        f_final.write(f'{data[0]} {data[1]} {data[2]} {data[3]} {data[4]}\n')
                        count_user = count_user + 1
                elif data[1] == message.from_user.first_name:
                    count_user = count_user + 1
                else:
                    with open('winners.txt', 'a', encoding='utf-8') as f_final:
                        f_final.write(f'{data[0]} {data[1]} {data[2]} {data[3]} {data[4]}\n')
        if count_user == 0:
            with open('winners.txt', 'a', encoding='utf-8') as f_final:
                f_final.write(f'Игрок: {message.from_user.first_name} Количество золота: {p.gold}\n')

        with open('winners_temp.txt', 'w+', encoding='utf-8') as f:
            f.seek(0)
        with open('winners.txt', encoding='utf-8') as f:
            content = f.read()
        bot.send_message(message.chat.id, f'Таблица успешных ребят:\n{content}')
        send = bot.send_message(message.chat.id, f'Сыграем еще раз?\nДа или Да?', reply_markup=keyboard_win)
        p.fullHealth()
        #monster.fullHealth()
        p.levelDowm()
        p.nullGold()
        bot.register_next_step_handler(send, battle, p)

        #bot.stop_polling()
    # else:
    #     bot.stop_polling()



#bot.polling(none_stop=True, interval=0)
if __name__ == '__main__':
    bot.skip_pending = True
    bot.polling()