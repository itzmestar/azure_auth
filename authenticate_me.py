from requests_oauthlib import OAuth2Session
import pickle
import os
import threading

#######
CLIENT_ID = '6656fdfs-0jg9-7643-45vb-hhg54dfs4'
CLIENT_SECRET = 'VSH/GDDGdss/h766dfd44g.hghfses2dfch@_'
AUTHORIZATION_BASE_URL = 'https://login.microsoftonline.com/'
TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
SCOPE = ["https://graph.microsoft.com/.default"]
REDIRECT_URI = 'https://localhost:8000/'
REFRESH_TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
REFRESH_TIME_SECONDS = 5
#######


class AzureAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.pickle_file = 'dont_delete.pickle'
        self.oauth_client = None
        self.authorization_url = None
        self.state = None
        self.token = None
        self.token_loader()
        self.ticker = threading.Event()

    def token_saver(self):
        with open(self.pickle_file, 'wb') as f:
            # Pickle the self.token using the highest protocol available.
            pickle.dump(self.token, f, pickle.HIGHEST_PROTOCOL)

    def token_loader(self):
        if not os.path.isfile(self.pickle_file):
            self.authorize()
            return
        with open(self.pickle_file, 'rb') as f:
            self.token = pickle.load(f)

    def authorize(self):
        self.oauth_client = OAuth2Session(self.client_id, scope=SCOPE, redirect_uri=REDIRECT_URI)
        self.authorization_url, self.state = self.oauth_client.authorization_url(AUTHORIZATION_BASE_URL)
        print("Please go here and authorize: {}".format(self.authorization_url))

        redirect_response = input("Copy & Paste the full redirect URL here then press 'Enter':")

        # Fetch the access token
        self.token = self.oauth_client.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=redirect_response)
        print(self.token)
        self.token_saver()

    def refresh_token(self):
        if self.token is None:
            self.token_loader()
            return
        self.oauth_client = OAuth2Session(self.client_id, token=self.token)
        extra = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        print("Refreshing token...")
        self.token = self.oauth_client.refresh_token(REFRESH_TOKEN_URL, **extra)
        print(self.token)
        self.token_saver()

    def get_access_token(self):
        return self.token['access_token']

    def run_refresh(self):
        while not self.ticker.wait(REFRESH_TIME_SECONDS):
            self.refresh_token()


def main():
    azure = AzureAuth(CLIENT_ID, CLIENT_SECRET)
    azure.run_refresh()


if __name__ == '__main__':
    main()
