import requests  
import datetime
import re
import string
import datetime
import pytz

from chat_handler import Chat


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
        # print('hour', hour)

        # check day time and send greeting
        if today == nowdata.day and 0 <= hour < 12:
            greet_bot.send_message(chat_id, '{}, {}'.format(greetings[0].capitalize(), name))

        elif today == nowdata.day and 12 <= hour < 17:
            greet_bot.send_message(chat_id, '{}, {}'.format(greetings[1].capitalize(), name))

        elif today == nowdata.day and 17 <= hour <= 23:
            greet_bot.send_message(chat_id, '{}, {}'.format(greetings[2].capitalize(), name))

        
ru_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
en_alphabet = 'abcdefghijklmnopqrstuvwxyz'

TOKEN = ''
greet_bot = BotHandler(TOKEN)
chat = Chat(greet_bot)

ru_greetings = ('здравствуй', 'привет', 'ку', 'здоров','здрасте','куку', 'здр','здаров','кукусики')  #Russian greeting words 
en_greetings = ('hello', 'hi', 'hey', 'whatsup')  # English greeting words

now = datetime.datetime.utcnow()
ru_bot_greetings = ('доброе утро', 'добрый день', 'добрый вечер')
en_bot_greetings = ('good morning', 'good afternoon', 'good evening')

# removing all punctuation signs and offtopic words from the line
def remove_extra(text):
    text = re.sub(r'what\'* *s *up','whatsup', text)  # substitute "what's up" written in any possible way to 'whatsup'
    text = re.split(r'[{}]'.format(string.punctuation), text.lower())  # remove punctuation
    text_words = ''.join(text).split()  # make a list of words
    for word in text_words:
        if re.match(r'\w*здорово*\w{1,2}\b', word): # delete such words as "выздоровел", "здоровый", "здоровая", etc, which meaning is about "health"
            text_words.remove(word)
    return text_words
        

def main():  
    chat.time_offset = chat.set_time_offset(greet_bot)
    print('time offset', chat.time_offset)
    

    while True:

        chat.update_info(greet_bot)

        all_rus_phrases = ru_greetings + ru_bot_greetings
        all_eng_phrases = en_greetings + en_bot_greetings

        user_greeted = False

        # list of all words from the message with no punctuation
        user_message_words = remove_extra(chat.last_text.lower())

        # check if there is any Russion greeting word in message
        for phrase in all_rus_phrases:
            if phrase in user_message_words or ((len(phrase) > 4) and phrase in chat.last_text.lower()):
                bot_greetings = ru_bot_greetings
                user_greeted = True
                break

        # check if there is any English greeting word in message    
        for phrase in all_eng_phrases:
            if phrase in user_message_words or ((len(phrase) > 4) and phrase in chat.last_text.lower()):
                bot_greetings = en_bot_greetings
                user_greeted = True
                break                        

        # if user sent message with no greeting            
        if not user_greeted:
            if user_message_words[0][0] in ru_alphabet:
                greet_bot.send_message(chat.last_id, 'Я умею только здороваться на русском и английском')
            elif user_message_words[0][0] in en_alphabet:
                greet_bot.send_message(chat.last_id, 'The only thing I can do is to greet people in Russian and English')
            else:
                greet_bot.send_message(chat.last_id, 'For now, I only understand English and Russian')
            chat.new_offset = chat.last_update_id + 1
            continue

        # greet user
        greet_bot.greet_user(now, chat.last_id, chat.last_name, bot_greetings,chat.time_offset)
        chat.new_offset = chat.last_update_id + 1

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()


