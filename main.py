import os
import pytz
#import keep_alive
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from main2 import makeImage, imageMaker
import telebot

import mysql.connector

mydb = mysql.connector.connect(
      host=os.getenv['HOST'],
      database=os.getenv['DATABASE'],
      user=os.getenv['USER'],
      password=os.getenv['PASS']
          )

mycursor = mydb.cursor()


#keep_alive.keep_alive()

IST = pytz.timezone('Asia/Kolkata')

chrome_options = Options()
WINDOW_SIZE = "1920,1080"
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options, keep_alive=True)
driver.get("http://fiitjeenorthwest.com/time_table.php")

try:
      myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'select')))
      print ("Page is ready!")
except TimeoutException:
      print ("Loading took too much time!")





x = str(datetime.datetime.now(IST))[:19]


def addEntry(msg, mycursor, mydb):
      name = str('' if msg.from_user.first_name is None else msg.from_user.first_name) + \
            str('' if msg.from_user.last_name is None else ' ' + msg.from_user.last_name)
      sql = "INSERT INTO visitors2 (Name, Chat_Id, Message, DateTime) VALUES (%s, %s, %s, %s)"
      val = (name, msg.chat.id, msg.text, x)
      mycursor.execute(sql, val)
      mydb.commit()


def addVisitTimes(chat_id, mycursor, mydb):
      #print("SELECT visits FROM visitors WHERE Chat_Id='" +str(chat_id) +"' ")
      mycursor.execute("SELECT visits FROM visitors WHERE Chat_Id='" +str(chat_id) +"' ")
      data= mycursor.fetchall()
      #print(data, data[0][0])
      visits=int(data[0][0])
      #print(visits)
      sql = "UPDATE visitors SET visits = "+str(visits+1)+" WHERE Chat_Id ="+str(chat_id)
      mycursor.execute(sql)
      mydb.commit()


def addVisitor(chat_id, name, mycursor, mydb):
      sql = "INSERT INTO visitors (Name, Chat_Id) VALUES (%s, %s)"
      val = (name, chat_id)
      mycursor.execute(sql, val)
      mydb.commit()
      addVisitTimes(chat_id, mycursor, mydb)


def checkVisitor(msg, mycursor, mydb):
      mycursor.execute("SELECT Chat_Id from visitors")
      data = mycursor.fetchall()
      allVisitors = [i[0] for i in data]
      #print(allVisitors)
      #print(type(msg))
      if msg.chat.id in allVisitors:
          addVisitTimes(msg.chat.id, mycursor, mydb)
      else:
          name = str('' if msg.from_user.first_name is None else msg.from_user.first_name)+\
                str('' if msg.from_user.last_name is None else ' '+msg.from_user.last_name)
          addVisitor(msg.chat.id, name, mycursor, mydb)


def setDefault(bot, msg, batch, mycursor, mydb):
      sql = "UPDATE visitors SET DefaultBatch = '" + batch + "' WHERE Chat_Id =" + str(msg.chat.id)
      mycursor.execute(sql)
      mydb.commit()
      bot.send_message(msg.chat.id, 'Default Batch set to '+batch)


def scheduleSetter(msg, mycursor, mydb):
      sql = "UPDATE visitors SET Scheduler = '1' WHERE Chat_Id =" + str(msg.chat.id)
      mycursor.execute(sql)
      mydb.commit()


def startMsg(bot, msg, mycursor, mydb):
      intro= "Hi, "+str('' if msg.from_user.first_name is None else msg.from_user.first_name)+ "! Welcome to the Fiitjee Punjabi Bagh Scheduler. \n\nYou can find your batch's Time-Table here without any need to .... you know:)\
              \n\nHere are some of the commands you may need.\
              \nBy the way how are you!:)\
              \n\n/Start - View this intro message again.\
              \n\n/Default_BatchCode - Set your BatchCode as default. \nEg. - /Default_NWCM123X1R  \
              \n\n/Send - Sends the Time table (when there is a default batch set). \
              \n\n/BatchCode - Sends the Time table of the given BatchCode.\nEg. - /NWCM123X1R\
              \n\n/Batchlist - Sends you the list of all Punjabi Bagh Batch.\
              \n\n-created by a Punjabi Bagh Student :D_"

      bot.send_message(msg.chat.id, intro)


def start(bot, batch, id, mycursor, mydb):

    element = Select(driver.find_element_by_tag_name('select'))
    try:
      element.select_by_value(batch)
      bot.send_message(id, "Sending Routine, Please wait!")
    except:
      bot.send_message(id, "No batch found.")
      return None

    driver.find_element_by_name('submit').click()
    sleep(3)
    table = driver.find_element_by_xpath('//*[@id="banner_flash1"]/div[3]/table[4]')
    rows = table.find_elements_by_tag_name('tr')
    
    lst = []
    for row in rows:
        columns = row.find_elements_by_tag_name('td')
        lst.append([i.text for i in columns])
        
    imageMaker(lst, batch)

    



    print('Image Created')
    bot.send_photo(id, photo=open('Schedule.png', 'rb'))
    print('image sent')


my_secret = os.getenv['Token']

bot = telebot.TeleBot(my_secret)

  # @bot.message_handler(commands=['Start'])
  # def greet(message):
  #     bot.reply_to(message, "Hey! Hows it going?")

@bot.message_handler(content_types="text")
def sender(message):
      if not mydb.is_connected():
        print('Database not connected to server')
        mydb.reconnect(attempts=10, delay=10)
      else: print('Database connected')
      
      checkVisitor(message, mycursor, mydb)
      addEntry(message, mycursor, mydb)
      upperMsg=message.text.upper()
      print(upperMsg +' - '+ str('' if message.from_user.first_name is None else message.from_user.first_name))
      

      if upperMsg=='/START' or upperMsg=='START':
          startMsg(bot, message, mycursor, mydb)

      elif upperMsg.startswith('DEFAULT_'):
          setDefault(bot, message, upperMsg[8:], mycursor, mydb)

      elif upperMsg.startswith('/DEFAULT_'):
          setDefault(bot, message, upperMsg[9:], mycursor, mydb)

      elif upperMsg == 'SEND' or upperMsg == '/SEND':
        try:
          mycursor.execute("SELECT DefaultBatch FROM visitors WHERE Chat_Id='" + str(message.chat.id) + "' ")
          data = mycursor.fetchall()
          #print(data, data[0][0])
          batch = data[0][0]
          if batch==None: raise
          start(bot, batch , message.chat.id, mycursor, mydb)
        except: 
          bot.send_message(message.chat.id, 'Please select your default batch')
          bot.send_message(message.chat.id, 'To set your BatchCode as default send \nDefault_BatchCode  \nEg. - Default_NWCM123X1R')
          return 0

        

      elif upperMsg == 'SCHEDULE' or upperMsg == '/SCHEDULE':
          scheduleSetter(message, mycursor, mydb)

      elif upperMsg == 'BATCHLIST' or upperMsg == '/BATCHLIST':
          options = driver.find_elements_by_tag_name('option')
          x = [i.get_attribute('value') for i in options]
          batches = ''
          for y in x:
              batches = batches + "\n" + y
          bot.send_message(message.chat.id, batches, mycursor, mydb)
      
      else:
        if upperMsg.startswith('/'): upperMsg=upperMsg[1:]
        start(bot, upperMsg , message.chat.id, mycursor, mydb)



try:
    bot.polling()
except Exception as e:
    print(e)
    bot = telebot.TeleBot(my_secret)
    #print('polling error')
    bot.polling()
