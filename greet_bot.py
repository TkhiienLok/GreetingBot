import requests  
import datetime
import re
import string

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
    
    def greet_user(self,nowdata, chat_id, name, greetings):
        today = nowdata.day
        hour = nowdata.hour

        # check day time and send greeting
        if today == nowdata.day and 0 <= hour < 12:
            greet_bot.send_message(chat_id, '{}, {}'.format(greetings[0].capitalize(), name))

        elif today == nowdata.day and 12 <= hour < 17:
            greet_bot.send_message(chat_id, '{}, {}'.format(greetings[1].capitalize(), name))

        elif today == nowdata.day and 17 <= hour <= 23:
            greet_bot.send_message(chat_id, '{}, {}'.format(greetings[2].capitalize(), name))


        
ru_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
en_alphabet = 'abcdefghijklmnopqrstuvwxyz'

greet_bot = BotHandler('716926010:AAExHWbqTeVcoaTvwN7qSqide8vLwN0Wd4s') 

ru_greetings = ('здравствуй', 'привет', 'ку', 'здоров','здрасте','здравствуйте','куку', 'здр')  #Russian greeting words 
en_greetings = ('hello', 'hi', 'hey', 'whatsup')  # English greeting words

now = datetime.datetime.now()
ru_bot_greetings = ('доброе утро', 'добрый день', 'добрый вечер')
en_bot_greetings = ('good morning', 'good afternoon', 'good evening')

# removing all punctuation signs
def remove_punctuation(text):
    remove = string.punctuation
    remove = remove.replace("-", "") # don't remove hyphens
    pattern = r"[{}]".format(remove) # create the pattern

    text = re.sub(pattern, " ", text) # substitute punctuation mark with space (in case there was no space between words)
    return text
    

def main():  
    new_offset = None

    while True:
        greet_bot.get_updates(new_offset)

        last_update = greet_bot.get_last_update()

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        all_rus_phrases = ru_greetings + ru_bot_greetings
        all_eng_phrases = en_greetings + en_bot_greetings

        user_greeted = False

        # all words from message
        user_message_words = remove_punctuation(last_chat_text.lower()).split()

        # check if there is any Russion greeting word in message
        for phrase in all_rus_phrases:
            if phrase in user_message_words or ((len(phrase) > 3) and phrase in last_chat_text.lower()):
                bot_greetings = ru_bot_greetings
                user_greeted = True
                break

        # check if there is any English greeting word in message    
        for phrase in all_eng_phrases:
            if phrase in user_message_words or ((len(phrase) > 3) and phrase in last_chat_text.lower()):
                bot_greetings = en_bot_greetings
                user_greeted = True
                break                        

        # if user sent message with no greeting            
        if not user_greeted:
            if last_chat_text.lower()[0] in ru_alphabet:
                greet_bot.send_message(last_chat_id, 'Я умею только здороваться')
            elif last_chat_text.lower()[0] in en_alphabet:
                greet_bot.send_message(last_chat_id, 'The only thing I can do is to greet people')
            else:
                greet_bot.send_message(last_chat_id, 'For now, I only understand English and Russion')
            new_offset = last_update_id + 1
            continue

        # greet user
        greet_bot.greet_user(now, last_chat_id, last_chat_name, bot_greetings)
        new_offset = last_update_id + 1

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()


