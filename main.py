# This code is based on https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example.html
from requests_oauthlib import OAuth2Session
import logging
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os

# SNI support for requests is needed.
# pip install requests[security]

# uncomment the following line to enable DEBUG logging
#logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

app = Flask(__name__)

# This information is obtained upon registration of a new Basecamp 3 Oauth app
# Basecamp API docs can be found here https://github.com/basecamp/bc3-api
# Register your Basecamp app using the following URI
# https://integrate.37signals.com/
# TODO update with your client ID
client_id = ""
# Do not share your secrets!
# TODO update with your client secret
client_secret = ""
authorization_base_url = 'https://launchpad.37signals.com/authorization/new'
token_url = 'https://launchpad.37signals.com/authorization/token'
# /etc/hosts entry as follows
# 127.0.0.1 bcamp.local
# TODO This must be customized based on your callback URI
bcamp_redirect_uri = 'http://bcamp.local:5000/callback'


# Allows for insecure (http) Oauth communication to bcamp.local. This is a security concern.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@app.route("/")
def demo():
    """Step 1: User Authorization.
    Redirect the user/resource owner to the OAuth provider (i.e. Basecamp)
    using an URL with a few key OAuth parameters.
    """
    basecampSession = OAuth2Session(client_id)
    basecampSession.redirect_uri = bcamp_redirect_uri
    authorization_url, state = basecampSession.authorization_url(authorization_base_url, type='web_server')

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
#    print(state)
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.
@app.route("/callback", methods=["GET"])
def callback():

    """ Step 3: Retrieving an access token.
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    basecampSession = OAuth2Session(client_id, state=session['oauth_state'])
    basecampSession.redirect_uri = bcamp_redirect_uri
    # TODO update the user-agent header with your apps user-agent
    basecampSession.headers.__setitem__('User-Agent','')
    basecampToken = basecampSession.fetch_token(token_url, code=request.args.get('code'), type='web_server', client_secret=client_secret)
    session['oauth_token'] = basecampToken

    return redirect(url_for('.profile'))

@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    basecampSession = OAuth2Session(client_id, token=session['oauth_token'])
    # TODO update the get with your project ID
    response = basecampSession.get('https://launchpad.37signals.com/authorization.json')
#    response = basecampSession.get('https://3.basecampapi.com/999999/projects.json')
    if response.status_code == 200 :
        return jsonify(response.json())
    else:
        return "A non 200 status code was returned from the server"


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)

