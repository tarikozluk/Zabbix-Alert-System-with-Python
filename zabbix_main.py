from pyzabbix import ZabbixAPI
from datetime import datetime, timedelta
from re import search
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
time_from = time_till - 60 * 60  # last 1 hour for now
"""
1 = Information
2 = Warning
3 = Avarage
4 = High
5 = Disaster
"""
try:

    problems = zapi.problem.get(selectTags="extend",
                                tags=[{'tag': 'Responsible', 'value': 'Companyname1'},
                                      {'tag': 'Responsible', 'value': 'Companyname2'}],
                                time_from=time_from,
                                severities=["2","3", "4", "5"],
                                #recent=["true", "false"],
                                recent="true",
                                time_till=time_till)
    for problem in problems:
        trigger = zapi.trigger.get(triggerids=problem['objectid'], selectHosts='extend')
        interface = zapi.hostinterface.get(hostids=trigger[0]['hosts'][0]['hostid'])
        group = zapi.hostgroup.get(hostids=trigger[0]['hosts'][0]['hostid'])
        enabled = "Enabled"
        # get value of trigger
        # print(problem)
        if trigger[0]['hosts'][0]['status'] == "1":
            enabled = "Disabled"
        timestamp = int(problem['clock'])
        dt_object = datetime.fromtimestamp(timestamp)
        #print(problem['r_clock'], problem['name'])
        resolvedtimestamp = int(problem['r_clock'])
        resolveddt_object = datetime.fromtimestamp(resolvedtimestamp)
        print("dt_object =", dt_object)


        ###if statement for RESPOSIBLE TAG
        if problem['tags'][0]['tag'] == "Responsible":
            responsible = problem['tags'][0]['value']
        elif problem['tags'][1]['tag'] == "Responsible":
            responsible = problem['tags'][1]['value']
        elif problem['tags'][2]['tag'] == "Responsible":
            responsible = problem['tags'][2]['value']
        elif problem['tags'][3]['tag'] == "Responsible":
            responsible = problem['tags'][3]['value']
        elif problem['tags'][4]['tag'] == "Responsible":
            responsible = problem['tags'][4]['value']
        else:
            responsible = "Zabbixte Belirtilmemiş"

        ###if statement for Istirak TAG
        if problem['tags'][0]['tag'] == "Istirak":
            istirak = problem['tags'][0]['value']
        elif problem['tags'][1]['tag'] == "Istirak":
            istirak = problem['tags'][1]['value']
        elif problem['tags'][2]['tag'] == "Istirak":
            istirak = problem['tags'][2]['value']
        elif problem['tags'][3]['tag'] == "Istirak":
            istirak = problem['tags'][3]['value']
        elif problem['tags'][4]['tag'] == "Istirak":
            istirak = problem['tags'][4]['value']
        else:
            istirak = "Zabbixte Belirtilmemiş"

        ###if statement for Action TAG
        if problem['tags'][0]['tag'] == "Action":
            action = problem['tags'][0]['value']
        elif problem['tags'][1]['tag'] == "Action":
            action = problem['tags'][1]['value']
        elif problem['tags'][2]['tag'] == "Action":
            action = problem['tags'][2]['value']
        elif problem['tags'][3]['tag'] == "Action":
            action = problem['tags'][3]['value']
        elif problem['tags'][4]['tag'] == "Action":
            action = problem['tags'][4]['value']
        else:
            action = "Zabbixte Belirtilmemiş"

        # severity settings
        if problem['severity'] == "4":
            Status_Severity = "High"
        elif problem['severity'] == "3":
            Status_Severity = "Average"
        elif problem['severity'] == "5":
            Status_Severity = "Disaster"
        elif problem['severity'] == "2":
            Status_Severity = "Warning"

        items = zapi.item.get(
            output="extend",
            hostids="{}".format(trigger[0]['hosts'][0]['hostid']),
            time_from=time_from,
            time_till=time_till,
            with_triggers='true',
            search={"key_": "vm.memory"})
        if problem['r_clock'] == "0":
            if dt_object > datetime.now() - timedelta(minutes=6):
                YollananVeri = (
                "Alarm Tarihi: {} \nSeviye: {} \nHost Grubu: {}\nHost: {}\nIP: {}\nProblem: {}\nAksiyon Tipi: {}\nSorumlu: {}\nİştirak: {}".format(
                    dt_object,
                    Status_Severity,
                    group[0]['name'],
                    trigger[0]['hosts'][0]['name'],
                    interface[0]['ip'],
                    # trigger[0]['description'],
                    problem['name'],
                    action,
                    responsible,
                    istirak))
                Araci.send_message(chat_id=Chat_ID, text=YollananVeri)

                #check 10 minutes ago for resolveddt_object
        else:
            if resolveddt_object > datetime.now() - timedelta(minutes=10):
                YollananVeri = (
                    "ALARM ÇÖZÜMLENDİ\nAlarm Çözümlenme Tarihi: {} \nSeviye: {} \nHost Grubu: {}\nHost: {}\nIP: {}\nÇözülen Problem: {}\nAksiyon Tipi: {}\nSorumlu: {}\nİştirak: {}".format(
                        resolveddt_object,
                        Status_Severity,
                        group[0]['name'],
                        trigger[0]['hosts'][0]['name'],
                        interface[0]['ip'],
                        # trigger[0]['description'],
                        problem['name'],
                        action,
                        responsible,
                        istirak))
                Araci.send_message(chat_id=Chat_ID, text=YollananVeri)
except Exception as e:
    print(e)
    Araci.send_message(chat_id=Chat_ID, text="error")

### Not finished, trying to improve for better efficiency by Zabbix API ###
### Momentane CPU-Werten werden auf das Code integriert werden. Dann braucht das Code für alle Fälle eine gute Beschreiung zB: CPU Problem=> Der letzte CPU-Wert
