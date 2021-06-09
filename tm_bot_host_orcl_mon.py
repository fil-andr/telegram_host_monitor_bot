import telebot
from mon_fuctions import *
import os
import platform
import re
import os


bot = telebot.TeleBot(os.environ['TEL_KEY'])


## read conf file
if platform.system() == 'Windows':
    with open(rf'{os.path.dirname(__file__)}\mon_bot.conf', 'r') as conf_file:
        hosts = conf_file.readlines()
if platform.system() == 'Linux':
    with open(rf'{os.path.dirname(__file__)}/mon_bot.conf', 'r') as conf_file:
        hosts = conf_file.readlines()
hosts_2 = []
for i in hosts:
    hosts_2.append(re.sub('\n','',i))

hosts = hosts_2

hosts_conn = []
for i in hosts:
    hosts_conn.append(i.split(','))

def help_message(hosts):
    help_message = 'hosts avaliable for monitor:\n'
    for host in hosts:
        host_name = host.split(',')[0]
        help_message +=f'/{host_name}\n'
    return help_message


def host_actual(input_string):
    inp = input_string.strip('/')
    host_actual_con = []
    for i in hosts_conn:
        if inp in i:
            host_actual_con.append(i[1])
            host_actual_con.append(i[2])
            host_actual_con.append(i[3])
    return host_actual_con

## build list of user  commands for edit message_text
hosts_lst_command = []
for i in hosts_conn:
    tmp_str = '/'
    tmp_str += i[0]
    hosts_lst_command.append(tmp_str)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "send /help for help ")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, help_message(hosts))
    elif message.text in hosts_lst_command:
        message_final = message.text.strip('/')
        bot.send_message(message.from_user.id, ssh_connect(host_actual(message_final)))
    else:
        bot.send_message(message.from_user.id, "send /help for help")


bot.polling(none_stop=True, interval=0)
