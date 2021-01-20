"""Authorization - ETrade Authorization API Calls

   TODO:
    * Lint this messy code
    * Catch events

    """

import logging
from rauth import OAuth1Service

# Set up logging
LOGGER = logging.getLogger(__name__)


class ETradeOAuth(object):
    """:description: Performs authorization for OAuth 1.0a

       :param client_key: Client key provided by Etrade
       :type client_key: str, required
       :param client_secret: Client secret provided by Etrade
       :type client_secret: str, required
       :param callback_url: Callback URL passed to OAuth mod, defaults to "oob"
       :type callback_url: str, optional
       :EtradeRef: https://apisb.etrade.com/docs/api/authorization/request_token.html

    """

    def __init__(self, consumer_key, consumer_secret, callback_url="oob"):

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url_prod = r"https://api.etrade.com"
        self.base_url_dev = r"https://apisb.etrade.com"
        self.req_token_url = r"https://api.etrade.com/oauth/request_token"
        self.auth_token_url = r"https://us.etrade.com/e/t/etws/authorize"
        self.access_token_url = r"https://api.etrade.com/oauth/access_token"
        self.callback_url = callback_url
        self.access_token = None
        self.resource_owner_key = None

    def get_request_token(self):
        """:description: Obtains the token URL from Etrade.

           :param None: Takes no parameters
           :return: Formatted Authorization URL (Access this to obtain taken)
           :rtype: str
           :EtradeRef: https://apisb.etrade.com/docs/api/authorization/request_token.html

        """

        # Set up session
        self.etrade = OAuth1Service(
            name="etrade",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            request_token_url="https://api.etrade.com/oauth/request_token",
            access_token_url="https://api.etrade.com/oauth/access_token",
            authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
            base_url="https://api.etrade.com")
        
        # Step 1: Get OAuth 1 request token and secret
        self.request_token, self.request_token_secret = self.etrade.get_request_token(
            params={"oauth_callback": "oob", "format": "json"})

        # Step 2: Go through the authentication flow. Login to E*TRADE.
        # After you login, the page will provide a text code to enter.
        authorize_url = self.etrade.authorize_url.format(self.etrade.consumer_key, self.request_token)
        LOGGER.debug(authorize_url)

        return authorize_url

    def get_access_token(self, verifier):
        """:description: Obtains access token. Requires token URL from :class:`get_request_token`

           :param verifier: OAuth Verification Code from Etrade
           :type verifier: str, required
           :return: OAuth access tokens
           :rtype: dict
           :EtradeRef: https://apisb.etrade.com/docs/api/authorization/get_access_token.html

        """
        # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
        self.session = self.etrade.get_auth_session(self.request_token,
                                      self.request_token_secret,
                                      params={"oauth_verifier": verifier})
        # Get access token
        self.access_token = {'oauth_token':self.request_token, 'oauth_token_secret':self.request_token_secret, 'oauth_verifier': verifier}
        LOGGER.debug(self.access_token)
        return self.access_token


class ETradeAccessManager(object):
    """:description: Renews and revokes ETrade OAuth access tokens

       :param client_key: Client key provided by Etrade
       :type client_key: str, required
       :param client_secret: Client secret provided by Etrade
       :type client_secret: str, required
       :param resource_owner_key: Resource key from :class:`ETradeOAuth`
       :type resource_owner_key: str, required
       :param resource_owner_secret: Resource secret from :class:`ETradeOAuth`
       :type resource_owner_secret: str, required
       :EtradeRef: https://apisb.etrade.com/docs/api/authorization/renew_access_token.html

    """

    def __init__(
        self, client_key, client_secret, resource_owner_key, resource_owner_secret, verifier
    ):
        self.client_key = client_key
        self.client_secret = client_secret
        self.resource_owner_key = resource_owner_key
        self.resource_owner_secret = resource_owner_secret
        self.renew_access_token_url = r"https://api.etrade.com/oauth/renew_access_token"
        self.revoke_access_token_url = (
            r"https://api.etrade.com/oauth/revoke_access_token"
        )
        self.verifier = verifier

        etrade = OAuth1Service(
            name="etrade",
            consumer_key=self.client_key,
            consumer_secret=self.client_secret,
            request_token_url="https://api.etrade.com/oauth/request_token",
            access_token_url="https://api.etrade.com/oauth/access_token",
            authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
            base_url="https://api.etrade.com")

        # Step 1: Get OAuth 1 request token and secret
        request_token, request_token_secret = etrade.get_request_token(
            params={"oauth_callback": "oob", "format": "json"})

        # Step 2: Exchange the authorized request token for an authenticated OAuth 1 session
        self.session = etrade.get_auth_session(request_token,
                                      request_token_secret,
                                      params={"oauth_verifier": verifier})

    def renew_access_token(self):
        """:description: Renews access tokens obtained from :class:`ETradeOAuth`

           :param None: Takes no parameters
           :return: Success or failure
           :rtype: bool (True or False)
           :EtradeRef: https://apisb.etrade.com/docs/api/authorization/renew_access_token.html

        """
        resp = self.session.get(self.renew_access_token_url)
        LOGGER.debug(resp.text)
        resp.raise_for_status()

        return True

    def revoke_access_token(self):
        """:description: Revokes access tokens obtained from :class:`ETradeOAuth`

           :param None: Takes no parameters
           :return: Success or failure
           :rtype: bool (True or False)
           :EtradeRef: https://apisb.etrade.com/docs/api/authorization/revoke_access_token.html

        """
        resp = self.session.get(self.revoke_access_token_url)
        LOGGER.debug(resp.text)
        resp.raise_for_status()

        return True
