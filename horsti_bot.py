# -*- coding: utf-8 -*-

# horstibot.py


T = "BOT_TOKEN"


















groups = {}

import os.path, pickle, hashlib, re
if os.path.isfile("HorstiBot_stats.dat"):
    #try:
    with open("HorstiBot_stats.dat", "rb") as f:
        groups = pickle.load(f)
    #except:
    #    pass
else:
    print("not a file")
    print("1-800-FIX-YOUR-SHIT")















SKIP = False
LOOKBACK_LETTER_COUNT = 5

import logging
import telegram
import time
from time import sleep

import sys, traceback

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError 

def save(reason):
    #if os.path.isfile("HorstiBot_stats.dat"):
        print("SAVING ",reason)
        with open("HorstiBot_stats.dat", "wb") as f:
            pickle.dump(groups, f)
        print("SAVED")

def main():
    update_id = None

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    bot = telegram.Bot(T)

    counter = 0
    rate_lim = False
    last_uid = None

    ij = 0
    try:
        while True:
            try:
                update_id = echo(bot, update_id)
                ij += 1
                if ij == 256:
                    ij = 0
                    save("/256 update")
                if last_uid == None:
                    last_uid = update_id
                elif update_id > last_uid:
                    rate_lim = False
                    counter = 0
                elif update_id == last_uid and SKIP:
                    print("Queue flushed")
                last_uid = update_id
            except telegram.TelegramError as e:
                if e.message in ("Bad Gateway", "Timed out"):
                    counter = 0
                    sleep(1)
                elif "Too many requests" in e.message:
                    counter += 1
                    print("Ratelimit: sleeping for ", 5*counter, " seconds")
                    sleep(5*counter)
                    rate_lim = True
                else:
                    counter = 0
                    raise e
            except KeyboardInterrupt as e:
                print("EXITING - DO NOT TERMINATE")
                save("Ctrl-C")
                return
            except URLError as e:
                sleep(1)
                counter = 0
            if not rate_lim:
                counter = 0
    except BaseException as e:
        save("Exception")
        raise e
            

import random, unicodedata, os
ALLOWABLE = ["Lc","Ll","Lm","Lo","Lt","Lu","Nd","Nl","No"]
COMMON_T = 0

def addMessage(message, g):
    w = [""] + list(message.lower()) + [""]
    lw = ""
    if "" not in g.keys():
        g[""] = []
    g[""].append(w[1])
    for i in range(1,len(w)-1):
        if w[i] != "\n":
            lw = (lw+w[i])[-LOOKBACK_LETTER_COUNT:]
            for j in range(0,len(lw)):
                lx = lw[j:]
                if lx not in g.keys():
                    g[lx] = []
                g[lx].append(w[i+1])

SPLIT_LINES = False
LAST_USER = {}

import os

def limit(s):
    t = " ".join(s.split(" ")[:50])
    return t[:400]

LANGS = ["af","an","bg","bs","ca","cs","cy","da","de","el","en","en-gb","en-sc","en-uk-north","en-uk-rp","en-uk-wmids","en-us","en-wi","eo","es","es-la","et","fa","fa-pin","fi","fr-be","fr-fr","ga","grc","hi","hr","hu","hy","hy-west","id","is","it","jbo","ka","kn","ku","la","lfn","lt","lv","mk","ml","ms","ne","nl","no","pa","pl","pt-br","pt-pt","ro","ru","sk","sq","sr","sv","sw","ta","tr","vi","vi-hue","vi-sgn","zh","zh-yue"]

def echo(bot, update_id):
    global COMMON_T

    for update in bot.getUpdates(offset=update_id, timeout=10):
        chat_id = update.message.chat_id
        update_id = update.update_id + 1
        message = update.message.text
        replyto = update.message.message_id
        user = update.message.from_user.id

        if chat_id not in groups.keys():
            groups[chat_id] = {}
                
        g = groups[chat_id]
        if 0 not in g.keys():
            g[0] = 1
        if 1 not in g.keys():
            g[1] = "en"
        if 2 not in g.keys():
            g[2] = 100
            
        curtime = time.time()
        t = (user, chat_id)
        
        if len(message) < 1:
            continue
        if message[0] == "/":
            rcmd = message.split(" ")[0].split("@")[0]
            cmd = rcmd.lower()
            if cmd == "/horsti":
                if SKIP: continue
                if t in LAST_USER.keys():
                    if (curtime - LAST_USER[t]) < g[0]:
                        continue
                    
                LAST_USER[t] = curtime
                COMMON_T += 1
                if COMMON_T == 8:
                    COMMON_T = 0
                if "" in g.keys():
                    msgs = []
                    for i in range(random.randint(1,3)):
                        while True:
                            lets = ""
                            lasttext = ""
                            nextc = "_"
                            while nextc != "" and len(lets) < 400:
                                trytext = lasttext
                                while random.random() < 0.33 or trytext not in g.keys():
                                    trytext = trytext[1:]
                                nextc = random.choice(g[trytext])
                                if nextc != "\n":
                                    lets += nextc
                                    lasttext = (lasttext + nextc)[-LOOKBACK_LETTER_COUNT:]
                                if random.random() < 0.25 and nextc == "":
                                    nextc = random.choice(g[""])
                                    lets += ". "+ nextc
                                    lasttext = (lasttext + nextc)[-LOOKBACK_LETTER_COUNT:]
                            msg = lets
                            if len(msg) > 0:
                                msgs.append(msg)
                                break
                    msg = "\n".join(msgs)
                    try:
                        bot.sendMessage(chat_id=chat_id,
                            text=msg)
                    except:
                        pass
                else:
                    bot.sendMessage(chat_id=chat_id,
                            text="[Chain is empty]",
                            reply_to_message_id=replyto)
            if cmd == "/horstilimit":
                if SKIP: continue
                t = " ".join(message.split(" ")[1:]).strip()
                if len(t) < 1:
                    bot.sendMessage(chat_id=chat_id,
                            text="[Usage: /horstilimit seconds]",
                            reply_to_message_id=replyto)
                    continue
                try:
                    v = int(t)
                except:
                    bot.sendMessage(chat_id=chat_id,
                            text="[Usage: /horstilimit seconds]",
                            reply_to_message_id=replyto)
                    continue
                if v <= 0 or v > 10000:
                    bot.sendMessage(chat_id=chat_id,
                            text="[limit must be between 1-10 000 seconds]",
                            reply_to_message_id=replyto)
                    continue
                bot.sendMessage(chat_id=chat_id,
                        text="[Limit set]",
                        reply_to_message_id=replyto)
                g[0] = v
            if cmd == "/horstittsspeed":
                if SKIP: continue
                t = " ".join(message.split(" ")[1:]).strip()
                if len(t) < 1:
                    bot.sendMessage(chat_id=chat_id,
                            text="[Usage: /horstittsspeed wpm]",
                            reply_to_message_id=replyto)
                    continue
                try:
                    v = int(t)
                except:
                    bot.sendMessage(chat_id=chat_id,
                            text="[Usage: /horstittsspeed wpm]",
                            reply_to_message_id=replyto)
                    continue
                if v < 80 or v > 500:
                    bot.sendMessage(chat_id=chat_id,
                            text="[Speed must be between 80-500 wpm]",
                            reply_to_message_id=replyto)
                    continue
                bot.sendMessage(chat_id=chat_id,
                        text="[Speed set]",
                        reply_to_message_id=replyto)
                g[2] = v
            if cmd == "/horsticlear":
                hash = hashlib.md5((str(chat_id)+str(user)+str(time.time()//1000)).encode("utf-8")).hexdigest()[:12].upper()
                what = ""
                try:
                    what = message.split(" ")[1].upper()
                except:
                    pass
                if what == hash:
                    groups[chat_id] = {}
                    bot.sendMessage(chat_id=chat_id,
                        text="[Messages cleared]",
                        reply_to_message_id=replyto)                    
                else:
                    bot.sendMessage(chat_id=chat_id,
                        text="[Copy this to confirm]\n/horsticlear " + hash,
                        reply_to_message_id=replyto)
            if cmd == "/horstitts":
                if t in LAST_USER.keys():
                    if (curtime - LAST_USER[t]) < max(5,g[0]):
                        continue
                LAST_USER[t] = curtime
                COMMON_T += 1
                if COMMON_T == 8:
                    COMMON_T = 0
                msgs = []
                while True:
                    lets = ""
                    lasttext = ""
                    nextc = "_"
                    while nextc != "" and len(lets) < 400:
                        trytext = lasttext
                        while random.random() < 0.33 or trytext not in g.keys():
                            trytext = trytext[1:]
                        nextc = random.choice(g[trytext])
                        if nextc != "\n":
                            lets += nextc
                            lasttext = (lasttext + nextc)[-LOOKBACK_LETTER_COUNT:]
                        if random.random() < 0.25 and nextc == "":
                            nextc = random.choice(g[""])
                            lets += ". "+ nextc
                            lasttext = (lasttext + nextc)[-LOOKBACK_LETTER_COUNT:]
                    msg = lets
                    if len(msg) > 0:
                        msgs.append(msg)
                        break
                msg = " ".join(msgs)
                def quoteEscape(s):
                    return s.replace("\\","\\\\").replace("\"","\\\"")
                try:
                    print("RM")
                    os.system("rm horsti.ogg 2>nul")
                    print("GEN")
                    os.system("espeak -s" + str(g[2]) + " -v" + g[1] + " \"" + limit(quoteEscape(msg)) + "\" --stdout | opusenc - horsti.ogg >nul 2>&1")
                    print("SEND")
                    bot.sendVoice(chat_id=chat_id,
                        voice=open("horsti.ogg","rb"))
                except BaseException as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print("\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                    bot.sendMessage(chat_id=chat_id,
                            text="Could not send voice",
                            reply_to_message_id=replyto)    
            if cmd == "/horstittslang":
                v = " ".join(message.split(" ")[1:]).strip()
                if v not in LANGS:
                    bot.sendMessage(chat_id=chat_id,
                            text=("[Unknown language]\n" if len(v) > 0 else "") + ", ".join(LANGS),
                            reply_to_message_id=replyto)
                    continue
                bot.sendMessage(chat_id=chat_id,
                        text="[Language set]",
                        reply_to_message_id=replyto)
                g[1] = v
        elif message[0] != "/":
            g = groups[chat_id]
            if SPLIT_LINES:
                for line in message.split("\n"):
                    addMessage(line, g)
            else:
                addMessage(message, g)
            
        
    sleep(0.5)
    return update_id
    
    
    
import logging

if __name__ == '__main__':
    while True:
        try:
            main()
            save("main")
            import sys
            sys.exit(0)
        except KeyboardInterrupt:
            input()
            import sys
            sys.exit(0)
        except SystemExit:
            break
        except BaseException as e:
            logging.exception(e)
            input()

