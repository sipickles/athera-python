from requests_oauthlib import OAuth2Session
import os
import time
import flask
import logging
import multiprocessing
import sys
if sys.version_info[0] < 3:  # pragma: no cover
    import Queue as queue
else:  # pragma: no cover
    import queue

class OAuthClient(object):
    """
    A helper class to perform OAuth2 authentication in Athera.

    Since OAuth2 receives HTTP callbacks from the Identity Provider, we run a simple Flask webserver to handle the flow. 
    The server is closed after fetch_token completes.

    When creating an OAuthClient, you need to provide a pre-registered client_id and client_secret. Register on Athera's
    Developer Dashboard: https://developer.athera.io/

    Usage:
        from oauth_client import OAuthClient
        	
        # Create the helper
        client = OAuthClient("<client_id>", "<client_secret>")
        # Begin the OAuth flow. Start the server in a subprocess and request the authorization URL.
	    authorize_url = client.authorize()
	    
        # Open authorize_url in a browser (an exercise for the reader)
        # The user will be asked to login, then grant permission for the application to access Athera via API.

        # Wait for the subprocess to report a token has been received
	    data = client.wait_for_auth()
        token = data['access_token']
        refresh_token = data['refresh_token']

        # Tokens last 24h. To manually refresh:
        data = client.refresh(access_token=token, refresh_token=refresh_token)
        token = data['access_token']
        refresh_token = data['refresh_token']
    """
    __authorize_endpoint = "authorize"
    __fetch_token_endpoint = "oauth/token"
    __callback_server_url = "http://localhost:5000/"
    __redirect_endpoint = "callback"
    __token_granted_endpoint = "complete"
    __idp_url = "https://id.athera.io/"
    __idp_audience = "https://public.athera.io"

    def __init__(self, 
            auth_client_id, 
            auth_client_secret, 
            idp_url=__idp_url,
            idp_audience=__idp_audience):
        super(OAuthClient, self).__init__()
        self.logger = logging.getLogger("AuthClient")
        self.auth_client_id = auth_client_id 
        self.auth_client_secret = auth_client_secret
        self.app = None
        self.server = None
        self.idp_url = idp_url
        self.idp_audience = idp_audience
        self.logger.info("Using {} {}".format(self.idp_url, self.idp_audience))

    def start_callback_server(self):
        self.logger.info("Setup CallbackServer")
        if self.server:
            return

        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

        self.queue = multiprocessing.Queue()
        self.server = multiprocessing.Process(target=run_flask_server)
        self.server.start()

    def stop_callback_server(self):
        self.logger.info("Stop CallbackServer")
        if not self.server:
            return

        self.server.terminate()
        self.server.join()

    def run_flask_server(self):
        app = flask.Flask("CallbackServer")
        app.secret_key = os.urandom(24)
        app.use_reloader = False
        app.debug = False
        app.add_url_rule("/" + self.__redirect_endpoint, "callback", self.route_callback)
        app.add_url_rule("/" + self.__token_granted_endpoint, "complete", self.route_token_granted)
        app.run()

    def authorize(self):
        self.logger.info("Authorize called")
        if not self.server:
            self.start_callback_server()

        self.logger.info("Creating Session")
        oauth_session = OAuth2Session(
            client_id=self.auth_client_id, 
            redirect_uri=self.__callback_server_url + self.__redirect_endpoint,
            scope=u"offline_access",
        )

        self.logger.info("Authorizing OAuth Session")
        authorization_url, state = oauth_session.authorization_url(
            url=self.idp_url + self.__authorize_endpoint,
            audience=self.idp_audience
        )
        return authorization_url

    def refresh(self, access_token, refresh_token):
        """
        Perform a manual refresh of the token
        """
        self.logger.info("Refresh called")

        extra = {
            'client_id': self.auth_client_id,
            'client_secret': self.auth_client_secret,
        }

        oauth_session = OAuth2Session(
            client_id=self.auth_client_id,
            token=access_token,
        )
        token = oauth_session.refresh_token(
            token_url=self.idp_url + self.__fetch_token_endpoint, 
            refresh_token=refresh_token,
            audience=self.idp_audience,
            **extra
        )
        self.logger.info("Refreshed token")
        return token

    def wait_for_auth(self):
        self.logger.info("Waiting for token...")
        try:
            token = self.queue.get(timeout=60)
            self.logger.info("Got token")
            # Wait enough time to allow route_token_granted to display in browser auth
            time.sleep(1)
            self.stop_callback_server()
            return token
        except queue.Empty:
            self.logger.info("Timeout")
            return None
        except KeyboardInterrupt:
            self.logger.info("Canceled")
            return None


    def route_callback(self, *args):
        """
        Runs in the Flask thread
        """
        oauth_session = OAuth2Session(
            client_id=self.auth_client_id, 
            redirect_uri=self.__callback_server_url + self.__token_granted_endpoint,
            token_updater=self.token_updated,
        )
        token = oauth_session.fetch_token(
            token_url=self.idp_url + self.__fetch_token_endpoint, 
            client_secret=self.auth_client_secret,
            #state=flask.session['oauth_state'],
            authorization_response=flask.request.url
        )
        #self.token_updated(token)
        self.queue.put(token)

        #return flask.Response(status=200, headers={})
        return flask.redirect(flask.url_for(self.__token_granted_endpoint))

    def route_token_granted(self, *args):
        self.logger.info("Token granted")
        data = "Authentication complete. You may now close this window"
        return flask.make_response(data, 200)

    def token_updated(self, token):
        self.logger.info("Token updated!")
        #self.token_update_callback(token)
        
        
