import requests  
import datetime
import re
import string
import datetime
import pytz


class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=100):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)]

        return last_update
    
    def greet_user(self,nowdata, chat_id, name, greetings,offset):
        today = nowdata.day
        hour = nowdata.hour + offset
        print('hour', hour)

        # check day time and send greeting
        if today == nowdata.day and 0 <= hour < 12:
            greet_bot.send_message(chat_id, '{}, {}'.format(greetings[0].capitalize(), name))

        elif today == nowdata.day and 12 <= hour < 17:
            greet_bot.send_message(chat_id, '{}, {}'.format(greetings[1].capitalize(), name))

        elif today == nowdata.day and 17 <= hour <= 23:
            greet_bot.send_message(chat_id, '{}, {}'.format(greetings[2].capitalize(), name))

                
ru_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
en_alphabet = 'abcdefghijklmnopqrstuvwxyz'

TOKEN = '716926010:AAExHWbqTeVcoaTvwN7qSqide8vLwN0Wd4s'
greet_bot = BotHandler(TOKEN) 

ru_greetings = ('здравствуй', 'привет', 'ку', 'здоров','здрасте','куку', 'здр','здаров','кукусики')  #Russian greeting words 
en_greetings = ('hello', 'hi', 'hey', 'whatsup')  # English greeting words

now = datetime.datetime.utcnow()
ru_bot_greetings = ('доброе утро', 'добрый день', 'добрый вечер')
en_bot_greetings = ('good morning', 'good afternoon', 'good evening')

# removing all punctuation signs and offtopic words
def remove_extra(text):
    text = re.sub(r'what\'* *s *up','whatsup', text)  # substitute "what's up" written in any possible way to 'whatsup'
    text = re.split(r'[{}]'.format(string.punctuation), text.lower())  # remove punctuation
    text_words = ''.join(text).split()  # make a list of words
    for word in text_words:
        if re.match(r'\w*здорово*\w{1,2}\b', word): # delete such words as "выздоровел", "здоровый", "здоровая", etc, which meaning is about "health"
            text_words.remove(word)
    return text_words


def check_zone(zone_text):
    tz = re.match(r'\w+ *-? *\w* *[/-]? *\w+ *[+-]? *\d*', zone_text)  # check format of user input
    tz_parts = []  
    if tz:
        tz = re.split(r'[{}]'.format(string.punctuation), zone_text.lower())
        tz_parts = ' '.join(tz).split()  # split user input to get just letters and digits
    print(tz_parts)

    time_zone_words = None
    for tz in pytz.all_timezones:   # defining time zone from pytz library
        current_tz = re.split(r'[{}]'.format(string.punctuation), tz.lower())
        current_tz_parts = ' '.join(current_tz).split()
        if current_tz_parts == tz_parts:
            time_zone_words = tz
    return time_zone_words


def set_time_offset():
    new_offset = None
    greet_bot.get_updates(new_offset)
    last_update = greet_bot.get_last_update()
    last_update_id = last_update['update_id']
    last_chat_text = last_update['message']['text']
    last_chat_id = last_update['message']['chat']['id']
    last_chat_name = last_update['message']['chat']['first_name']
    last_few_words = last_chat_text[:15]

    msg = "Hey, {}, before talking about \" {}...bla, bla, bla\", could we set up time first? I'd appriciate if you enter your time zone (you can use either spaces or dashes or slashes in your input)".format(last_chat_name, last_few_words)

    greet_bot.send_message(last_chat_id, msg)
    new_offset = last_update_id + 1

    greet_bot.get_updates(new_offset)
    last_update = greet_bot.get_last_update()
    last_update_id = last_update['update_id']
    last_chat_text = last_update['message']['text']
    new_offset = last_update_id + 1
    timezone = check_zone(last_chat_text)
    print(timezone)
    
    while not timezone:
        greet_bot.send_message(last_chat_id, 'Enter a valid time zone, please')
        new_offset = last_update_id + 1

        greet_bot.get_updates(new_offset)
        last_update = greet_bot.get_last_update()
        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        timezone = check_zone(last_chat_text)
        new_offset = last_update_id + 1
            
    
    est = pytz.timezone(timezone)
    now = datetime.datetime.utcnow()
    time_zone_offset = str(est.localize(now).utcoffset()).split(':')[0]

    greet_bot.send_message(last_chat_id, 'Now, I am all set up, thanks')
    return int(time_zone_offset)
    

def main():  
    new_offset = None
    time_offset = set_time_offset()
    print('time offset', time_offset)
    

    while True:
        greet_bot.get_updates(new_offset)

        last_update = greet_bot.get_last_update()

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']
        last_chat_surname = last_update['message']['chat']['last_name']

        all_rus_phrases = ru_greetings + ru_bot_greetings
        all_eng_phrases = en_greetings + en_bot_greetings

        user_greeted = False

        # list of all words from the message with no punctuation
        user_message_words = remove_extra(last_chat_text.lower())

        # check if there is any Russion greeting word in message
        for phrase in all_rus_phrases:
            if phrase in user_message_words or ((len(phrase) > 4) and phrase in last_chat_text.lower()):
                bot_greetings = ru_bot_greetings
                user_greeted = True
                break

        # check if there is any English greeting word in message    
        for phrase in all_eng_phrases:
            if phrase in user_message_words or ((len(phrase) > 4) and phrase in last_chat_text.lower()):
                bot_greetings = en_bot_greetings
                user_greeted = True
                break                        

        # if user sent message with no greeting            
        if not user_greeted:
            if user_message_words[0][0] in ru_alphabet:
                greet_bot.send_message(last_chat_id, 'Я умею только здороваться на русском и английском')
            elif user_message_words[0][0] in en_alphabet:
                greet_bot.send_message(last_chat_id, 'The only thing I can do is to greet people in Russian and English')
            else:
                greet_bot.send_message(last_chat_id, 'For now, I only understand English and Russian')
            new_offset = last_update_id + 1
            continue

        # greet user
        greet_bot.greet_user(now, last_chat_id, last_chat_name, bot_greetings,time_offset)
        new_offset = last_update_id + 1

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()


