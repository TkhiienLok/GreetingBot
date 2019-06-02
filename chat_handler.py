import string
import re
import pytz
import datetime


class Chat:
    
    def __init__(self, bot):
        self.last_update_id = None
        self.last_text = None
        self.last_id = None
        self.last_name = None
        self.last_surname = None
        self.time_offset = 0
        self.timezone = 'UTC'
        self.new_offset = None
        self.update_info(bot)
        self.started = False

    def update_info(self, bot): # updates chat information about last user's message
        bot.get_updates(self.new_offset)
        last_update = bot.get_last_update()
        self.last_update_id = last_update['update_id']
        self.last_text = last_update['message']['text']
        self.last_id = last_update['message']['chat']['id']
        self.last_name = last_update['message']['chat']['first_name']
        self.last_surname = last_update['message']['chat']['last_name']
        #print(last_update['message']['date'])  # message date in seconds


    def check_zone(self,zone_text): # check if the input string is a valid time zone and if it is then returns time zone in pytz format 
        tz = re.match(r'\w+ *-? *\w* *[/-]? *\w+ *[+-]? *\d*', zone_text)  # check format of user input
        tz_parts = []
        if tz:
            tz = re.split(r'[{}]'.format(string.punctuation), zone_text.lower())
            tz_parts = ' '.join(tz).split()  # split user input to get just letters and digits
        # print(tz_parts)

        time_zone_words = None
        for tz in pytz.all_timezones:   # looking up input time zone in the timezone list of the pytz library
            current_tz = re.split(r'[{}]'.format(string.punctuation), tz.lower())
            current_tz_parts = ' '.join(current_tz).split()
            if current_tz_parts == tz_parts:
                time_zone_words = tz
        return time_zone_words

    def set_time_offset(self, bot):  # asking user to input time zone and setting it up  
        self.update_info(bot)
        last_few_words = self.last_text[:15]
        if self.started:
            msg = "Hey, {}, before talking about \" {}...bla, bla, bla\", could we set up time first? I'd appriciate \
if you enter your time zone (you can use either spaces or dashes or slashes in your input)".format(self.last_name, last_few_words)
        else:
            msg = "Hi, {} {}, I am Greeting Bot. My job is to greet people. I'll be glad to hear from you, but for now, \
I need us to set up time first. I'd appriciate if you'd enter your time zone (you can use either spaces or dashes or slashes \
in your input)".format(self.last_name, self.last_surname)

            self.started = True

        bot.send_message(self.last_id, msg)
        self.new_offset = self.last_update_id + 1

        self.update_info(bot)
        self.new_offset = self.last_update_id + 1
        timezone = self.check_zone(self.last_text)
        print(timezone)
        
        while not timezone:  # while user inputs invalid value for time zone ask it again
            bot.send_message(self.last_id, 'Enter a valid time zone, please')
            self.new_offset = self.last_update_id + 1

            self.update_info(bot)
            
            timezone = self.check_zone(self.last_text)
            self.new_offset = self.last_update_id + 1
                
        
        self.timezone = pytz.timezone(timezone)  # set up time zone for chat
        now = datetime.datetime.utcnow()
        time_zone_offset = str(self.timezone.localize(now).utcoffset()).split(':')[0]  # getting hours offset from datetime.utcnow()

        bot.send_message(self.last_id, 'Now, I am all set up, thanks')
        self.time_offset = int(time_zone_offset)
        
        return self.time_offset
    
