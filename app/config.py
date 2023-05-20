import os

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_1539_cloud:1234567890@std-mysql.ist.mospolytech.ru/std_1539_cloud'
#SQLALCHEMY_DATABASE_URI = 'mysql://vladimirmilor:Sinox2023@rc1a-c52y6tycx7futkte.mdb.yandexcloud.net:3306/db-miloradov-project?ssl_ca=CA.pem'
SECRET_KEY = '72f5a72a25d8d5f5a10a9fd21eeec4b2cb347e839c82b061e4ff5e6ad5011b88'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')

ADMIN_ROLE_ID = 1
MODER_ROLE_ID = 2
USER_ROLE_ID = 3