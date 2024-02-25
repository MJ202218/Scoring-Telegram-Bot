from telegram import ReplyKeyboardMarkup

class User:
    def __init__(self, fullname,userid, username, role):
        self.fullname = fullname
        self.userid = userid
        self.username = username
        self.role = role
        self.start_Keyboard()
    def start_Keyboard(self):
        if self.role == 'ADMIN':
            self.keyboard= [
                ["Score registriation"],
                ["hello", 'e']
            ]
        else:
            self.keyboard= [
                ['مشاهده نمرات']
         ]
    def get_keyboard(self):
        return ReplyKeyboardMarkup(self.keyboard, resize_keyboard=True , one_time_keyboard=True)