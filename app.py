from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Franchise, Player, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Gamers NBA Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///gamersnba.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                  for x in xrange(32))
  login_session['state'] = state
  # return "The current session state is %s" % login_session['state']
  return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  access_token = request.data
  print "access token received %s " % access_token

  app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
      'web']['app_id']
  app_secret = json.loads(
      open('fb_client_secrets.json', 'r').read())['web']['app_secret']
  url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
      app_id, app_secret, access_token)
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]

  # Use token to get user info from API
  userinfo_url = "https://graph.facebook.com/v2.8/me"
  '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
  token = result.split(',')[0].split(':')[1].replace('"', '')

  url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  # print "url sent for API access:%s"% url
  # print "API JSON result: %s" % result
  data = json.loads(result)
  login_session['provider'] = 'facebook'
  login_session['username'] = data["name"]
  login_session['email'] = data["email"]
  login_session['facebook_id'] = data["id"]

  # The token must be stored in the login_session in order to properly logout
  login_session['access_token'] = token

  # Get user picture
  url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  data = json.loads(result)

  login_session['picture'] = data["data"]["url"]

  # see if user exists
  user_id = getUserID(login_session['email'])
  if not user_id:
    user_id = createUser(login_session)
  login_session['user_id'] = user_id

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']

  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

  flash("Now logged in as %s" % login_session['username'])
  return output


@app.route('/fbdisconnect')
def fbdisconnect():
  facebook_id = login_session['facebook_id']
  # The access token must me included to successfully logout
  access_token = login_session['access_token']
  url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
  h = httplib2.Http()
  result = h.request(url, 'DELETE')[1]
  return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
  # Validate state token
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  # Obtain authorization code
  code = request.data

  try:
    # Upgrade the authorization code into a credentials object
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_response(
        json.dumps('Failed to upgrade the authorization code.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Check that the access token is valid.
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
         % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  # If there was an error in the access token info, abort.
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 500)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Verify that the access token is used for the intended user.
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(
        json.dumps("Token's user ID doesn't match given user ID."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Verify that the access token is valid for this app.
  if result['issued_to'] != CLIENT_ID:
    response = make_response(
        json.dumps("Token's client ID does not match app's."), 401)
    print "Token's client ID does not match app's."
    response.headers['Content-Type'] = 'application/json'
    return response

  stored_access_token = login_session.get('access_token')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_access_token is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps('Current user is already connected.'),
                             200)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Store the access token in the session for later use.
  login_session['access_token'] = credentials.access_token
  login_session['gplus_id'] = gplus_id

  # Get user info
  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt': 'json'}
  answer = requests.get(userinfo_url, params=params)

  data = answer.json()

  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']
  # ADD PROVIDER TO LOGIN SESSION
  login_session['provider'] = 'google'

  # see if user exists, if it doesn't make a new one
  user_id = getUserID(data["email"])
  if not user_id:
    user_id = createUser(login_session)
  login_session['user_id'] = user_id

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']
  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
  flash("you are now logged in as %s" % login_session['username'])
  print "done!"
  return output

# User Helper Functions


def createUser(login_session):
  newUser = User(name=login_session['username'], email=login_session[
                 'email'], picture=login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(User).filter_by(email=login_session['email']).one()
  return user.id


def getUserInfo(user_id):
  user = session.query(User).filter_by(id=user_id).one()
  return user


def getUserID(email):
  try:
    user = session.query(User).filter_by(email=email).one()
    return user.id
  except:
    return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
  # Only disconnect a connected user.
  access_token = login_session.get('access_token')
  if access_token is None:
    response = make_response(
        json.dumps('Current user not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]
  if result['status'] == '200':
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
  else:
    response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    response.headers['Content-Type'] = 'application/json'
    return response


# JSON APIs to view Restaurant Information
@app.route('/franchise/<int:franchise_id>/roster/JSON')
def rosterJSON(franchise_id):
  franchise = session.query(Franchise).filter_by(id=franchise_id).one()
  roster = session.query(Player).filter_by(
      franchise_id=franchise_id).all()
  return jsonify(Roster=[r.serialize for r in roster])


@app.route('/franchise/<int:franchise_id>/roster/<int:player_id>/JSON')
def playerProfileJSON(franchise_id, player_id):
  Player_Profile = session.query(Player).filter_by(id=player_id).one()
  return jsonify(Player_Profile=Player_Profile.serialize)


@app.route('/franchise/JSON')
def restaurantsJSON():
  franchises = session.query(Franchise).all()
  return jsonify(Franchises=[f.serialize for f in franchises])


# Show all Franchises
@app.route('/')
@app.route('/franchise/')
def displayFranchises():
  franchises = session.query(Franchise).order_by(asc(Franchise.name))
  if 'username' not in login_session:
    return render_template('publicfranchises.html', franchises=franchises)
  else:
    return render_template('franchises.html', franchises=franchises)

# Create/buy a new franchise


@app.route('/franchise/new/', methods=['GET', 'POST'])
def newFranchise():
  if 'username' not in login_session:
    return redirect('/login')
  if request.method == 'POST':
    newclub = Franchise(
        name=request.form['name'], user_id=login_session['user_id'])
    session.add(newclub)
    flash('%s Your New Basketball Franchise has been Successfully Negotiated. Congratulations you are now a Franchise owner' % newclub.name)
    session.commit()
    return redirect(url_for('displayFranchises'))
  else:
    return render_template('newfranchise.html')

# Rename a franchise


@app.route('/franchise/<int:franchise_id>/edit/', methods=['GET', 'POST'])
def editFranchise(franchise_id):
  franchiseToRename = session.query(
      Franchise).filter_by(id=franchise_id).one()
  if 'username' not in login_session:
    return redirect('/login')
  if franchiseToRename.user_id != login_session['user_id']:
    return "<script>function myFunction() {alert('You are not authorized to franchise. You must own a franchise to edit one.');}</script><body onload='myFunction()'>"
  if request.method == 'POST':
    if request.form['name']:
      franchiseToRename.name = request.form['name']
      flash('Your Franchise has been Successfully renamed as %s' % franchiseToRename.name)
      return redirect(url_for('displayFranchises'))
  else:
    return render_template('editfranchise.html', franchise=franchiseToRename)


# Delete a franchise
@app.route('/franchise/<int:franchise_id>/delete/', methods=['GET', 'POST'])
def deleteFranchise(franchise_id):
  franchiseToDelete = session.query(
      Franchise).filter_by(id=franchise_id).one()
  if 'username' not in login_session:
    return redirect('/login')
  if franchiseToDelete.user_id != login_session['user_id']:
    return "<script>function myFunction() {alert('You are not authorized to delete this Franchise. You have to be a franchise owner before you can delete!');}</script><body onload='myFunction()'>"
  if request.method == 'POST':
    session.delete(franchiseToDelete)
    flash('%s no longer exists as a franchise' % franchiseToDelete.name)
    session.commit()
    return redirect(url_for('displayFranchises', franchise_id=franchise_id))
  else:
    return render_template('deletefranchise.html', franchise=franchiseToDelete)

# Show a franchise roster


@app.route('/franchise/<int:franchise_id>/')
@app.route('/franchise/<int:franchise_id>/roster/')
def displayRoster(franchise_id):
  franchise = session.query(Franchise).filter_by(id=franchise_id).one()
  creator = getUserInfo(franchise.user_id)
  roster = session.query(Player).filter_by(
      franchise_id=franchise_id).all()
  if 'username' not in login_session or creator.id != login_session['user_id']:
    return render_template('publicroster.html', roster=roster, franchise=franchise, creator=creator)
  else:
    return render_template('roster.html', roster=roster, franchise=franchise, creator=creator)


# Create a new player
@app.route('/franchise/<int:franchise_id>/roster/new/', methods=['GET', 'POST'])
def newPlayer(franchise_id):
  if 'username' not in login_session:
    return redirect('/login')
  franchise = session.query(Franchise).filter_by(id=franchise_id).one()
  if login_session['user_id'] != franchise.user_id:
    return "<script>function myFunction() {alert('You are not authorized to add menu player to this franchise. You must be a franchise owner to add players.');}</script><body onload='myFunction()'>"
  print 'its okay here at 1'
  if request.method == 'POST':
    newPlayer = Player(
        name=request.form['name'],
        age=request.form['age'],
        price=request.form['price'],
        position=request.form['position'],
        height=request.form['height'],
        weight=request.form['weight'],
        image=request.form['image'],
        # ppg=request.form['ppg'],
        # youtube_url=request.form['youtube_url'],
        franchise_id=franchise_id,
        user_id=login_session['user_id'])
    session.add(newPlayer)
    session.commit()
    flash('%s has been Successfully Created' % (newPlayer.name))
    return redirect(url_for('displayRoster', franchise_id=franchise_id))
  else:
    return render_template('newplayer.html', franchise_id=franchise_id)

# Edit a Player Profile


@app.route('/franchise/<int:franchise_id>/roster/<int:player_id>/edit', methods=['GET', 'POST'])
def editPlayer(franchise_id, player_id):
  if 'username' not in login_session:
    return redirect('/login')
  profileToEdit = session.query(Player).filter_by(id=player_id).one()
  franchise = session.query(Franchise).filter_by(id=franchise_id).one()
  if login_session['user_id'] != franchise.user_id:
    return "<script>function myFunction() {alert('You are not authorized to edit a player profile. You have to own a franchise to edit the profile of a player!');}</script><body onload='myFunction()'>"
  if request.method == 'POST':
    if request.form['name']:
      profileToEdit.name = request.form['name']
    if request.form['age']:
      profileToEdit.age = request.form['age']
    if request.form['price']:
      profileToEdit.price = request.form['price']
    if request.form['height']:
      profileToEdit.height = request.form['height']
    if request.form['position']:
      profileToEdit.position = request.form['position']
    if request.form['weight']:
      profileToEdit.weight = request.form['weight']
    if request.form['image']:
      profileToEdit.image = request.form['image']
    # if request.form['youtube_url']:
    #   editedPlayer.youtube_url = request.form['youtube_url']
    # if request.form['ppg']:
    #   editedPlayer.ppg = request.form['ppg']
    session.add(profileToEdit)
    session.commit()
    flash('Player Profile Successfully Edited')
    return redirect(url_for('displayRoster', franchise_id=franchise_id))
  else:
    return render_template('editplayerprofile.html', franchise=franchise, player=profileToEdit)


# Delete a player
@app.route('/franchise/<int:franchise_id>/roster/<int:player_id>/delete', methods=['GET', 'POST'])
def deletePlayerProfile(franchise_id, player_id):
  if 'username' not in login_session:
    return redirect('/login')
  franchise = session.query(Franchise).filter_by(id=franchise_id).one()
  profileToDelete = session.query(Player).filter_by(id=player_id).one()
  if login_session['user_id'] != franchise.user_id:
    return "<script>function myFunction() {alert('You are not authorized to delete this player's profile. You must be a franchise owner in order to delete a player's profile.');}</script><body onload='myFunction()'>"
  if request.method == 'POST':
    session.delete(profileToDelete)
    session.commit()
    flash('%s\'s Profile has been Successfully Deleted' % profileToDelete.name)
    return redirect(url_for('displayRoster', franchise_id=franchise_id))
  else:
    return render_template('deleteplayerprofile.html', profile=profileToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
  if 'provider' in login_session:
    if login_session['provider'] == 'google':
      gdisconnect()
      del login_session['gplus_id']
      del login_session['access_token']
    if login_session['provider'] == 'facebook':
      fbdisconnect()
      del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    flash("You have successfully been logged out.")
    return redirect(url_for('displayFranchises'))
  else:
    flash("You were not logged in")
    return redirect(url_for('displayFranchises'))


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host='0.0.0.0', port=5000)
