sys.path.append('../../pyetrade/pyetrade/')
import collect_data

config = configparser.ConfigParser()
config.read('config.ini')

import pyetrade

consumer_key = "<CONSUMER_KEY>"
consumer_secret = "<SECRET_KEY>"

oauth = pyetrade.ETradeOAuth(consumer_key, consumer_secret)
print(oauth.get_request_token())  # Use the printed URL

verifier_code = input("Enter verification code: ")
tokens = oauth.get_access_token(verifier_code)
print(tokens)