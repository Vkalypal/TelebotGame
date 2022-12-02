import telebot
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

    def fullHealth(self):
        self._health = self._fullHealth


class Player(Creature):
    __level = 1

    def levelUp(self):
        self.__level = self.__level + 1
        self._damage = self._damage + 1

    def hasWon(self):
        if self.__level == 20:
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


def attackPlayer(message, m):
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
    bot.send_message(message.chat.id, f'Здоровье {m.name} = {m.health}')
    if (m.isDead() == True):
        bot.send_message(message.chat.id, f'Вы убили {m.name}.')
        p.levelUp()
        bot.send_message(message.chat.id, f'Ваш уровень {p.level}.')
        bot.send_message(message.chat.id, f'Вы нашли {m.gold} золотых.')
        p.addGold(m.gold)


def playerisDead(message):
    bot.send_message(message.chat.id, f'Вы достигли {p.level} '
        f'уровня и унесли с собой в могилу {p.gold} золотых.')
    bot.stop_polling()


#@bot.message_handler(content_types=['text'])
def choiceBattle(message, monster):
    print('Кого я встретил на самом деле ' + monster.name)
    if (p.isDead() != True and monster.isDead() != True):
        msg = message.text.lower()
        if msg == 'бежать':
            if (random.randint(0, 1) == 1):
                bot.send_message(message.chat.id, 'Вы сбежали')
                print('ты сбежал от ' + monster.name)
                monster.fullHealth()
                send = bot.send_message(message.chat.id, 'Продолжим?')
                bot.register_next_step_handler(send, battle)
                return
            else:
                bot.send_message(message.chat.id, 'Вам не удалось сбежать')
                attackPlayer(message, monster)
                if p.isDead() == True:
                    bot.send_message(message.chat.id, 'ТЫ МЕРТВЕТС!!!')
                    bot.register_next_step_handler(message, playerisDead)
                    return
                send = bot.send_message(message.chat.id, 'Бежать или драться?')
                bot.register_next_step_handler(send, choiceBattle, monster)
        if msg == 'драться':
            attackMonster(message, monster, p)
            attackPlayer(message, monster)
            if p.isDead() == True:
                bot.send_message(message.chat.id, 'ТЫ МЕРТВЕТС!!!')
                bot.register_next_step_handler(message, playerisDead)
                return
            if monster.isDead():
                monster.fullHealth()
                send = bot.send_message(message.chat.id, 'Продолжим?')
                bot.register_next_step_handler(send, battle)
                return
            send = bot.send_message(message.chat.id, 'Бежать или драться?')
            bot.register_next_step_handler(send, choiceBattle, monster)
    else:
        bot.send_message(message.chat.id, 'ТЫ МЕРТВЕТС!!!')
        bot.register_next_step_handler(message, playerisDead)


p = Player('Nikita', '@', 10, 1, 0)


@bot.message_handler(func=lambda message: message.text.lower() == 'играть')
def battle(message):
    #while (p.isDead() != True and p.hasWon() != True):
    if (p.isDead() != True and p.hasWon() != True):
        bot.send_message(message.chat.id, 'Нет пути назад')
        monster = randomMonsters()
        bot.send_message(message.chat.id, f'Вы встретили {monster.name}')
        print('Вы встретили ' + monster.name + ' (' + monster.simbol + ')')
        bot.send_message(message.chat.id, f'Здоровье {monster.name} {monster.health}')
        bot.send_message(message.chat.id, f'Ваше здоровье {p.health} .')
        send = bot.send_message(message.chat.id, 'Бежать или драться?')
        bot.register_next_step_handler(send, choiceBattle, monster)
    elif p.hasWon() == True:
        bot.send_message(message.chat.id, f'ВЫ ПОБЕДИЛЕ и заработали '
                                          f'{p.gold} монет.')
        bot.stop_polling()
    else:
        bot.stop_polling()


#bot.infinity_polling()
bot.polling(none_stop=True, interval=0)
#if __name__ == '__main__':
#    bot.skip_pending = True
#    bot.polling()