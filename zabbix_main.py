from pyzabbix import ZabbixAPI
from datetime import datetime
import time
import logging
import telebot  # Successfully installed pyTelegramBotAPI-4.6.1
import time
import os
from dotenv import load_dotenv

load_dotenv()
Bot_Token = os.getenv("BOT_TOKEN")
Chat_ID = os.getenv("CHAT_ID")

Araci = telebot.TeleBot(Bot_Token)

zapi = ZabbixAPI(os.getenv("ZABBIX_URL"))
zapi.login(os.getenv("ZABBIX_USERNAME"), os.getenv("ZABBIX_PASSWORD"))
time_till = time.mktime(datetime.now().timetuple())
time_from = time_till - 60 * 60*192# last 8 days for now


"""
1 = Information
2 = Warning
3 = Avarage
4 = High
5 = Disaster
"""
try:

    problems = zapi.problem.get(selectTags="extend",
                                tags=[{'tag': 'Responsible', 'value': 'Euromessage'}],
                                time_from=time_from,
                                severities=["2","3"],
                                recent = ["true","false"],
                                time_till=time_till)
    for problem in problems:
        trigger = zapi.trigger.get(triggerids=problem['objectid'], selectHosts='extend')
        interface = zapi.hostinterface.get(hostids=trigger[0]['hosts'][0]['hostid'])
        group = zapi.hostgroup.get(hostids=trigger[0]['hosts'][0]['hostid'])
        enabled = "Enabled"

        if trigger[0]['hosts'][0]['status'] == "1":
            enabled = "Disabled"

        YollananVeri = ("Group: {}\n Host: {}\n IP: {}\n Problem: {}\n {}\n Responsible: {}\n İştirak: {}\n".format(group[0]['name'],
                                                                                  trigger[0]['hosts'][0]['host'],
                                                                                  interface[0]['ip'],
                                                                                  trigger[0]['description'],
                                                                                  enabled,
                                                                                  problems[0]['tags'][2]['value'],
                                                                                  problems[0]['tags'][1]['value']))
        Araci.send_message(chat_id=Chat_ID,text=YollananVeri)
        print(problems[0]['tags'][2]['value'])
except Exception as e:
    print(e)
    Araci.send_message(chat_id=Chat_ID,text="error")


### Not finished, trying to improve for better efficiency by Zabbix API ###