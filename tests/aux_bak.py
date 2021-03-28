from models.constants import Constants, Literal_Constants
from models.database import Database

print(Constants.DBStatements.DB_LAN_READ % ("'6216877'"))
db = Database('localhost', 'ttsbot', 'fanialiciA1!', 'ttsbot')
print(db)
#print(db.connection._cmysql.escape("how are you'dddd"))
#a = db.read_one(Constants.DBStatements.DB_AUDIO_READ_FOR_CHECKING, ('6216877', "how are you'dddd"))
#print(a)