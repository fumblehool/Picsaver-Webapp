from flask import Flask, render_template, request, redirect \
, session
from instagram.client import InstagramAPI
from instagram import client, subscriptions
import secret

#app configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = secret.secret_key

api = InstagramAPI(**secret.secrets)

@app.route("/")
def main():
	if "access_token" in session:
		return render_template("call.html")
	else:
		return render_template("index.html")


@app.route("/connect")
def connect():
	url = api.get_authorize_url(scope=["likes","comments"])
	#redirect user to instagram login and asks permission
	return redirect(url)


@app.route('/instagram_callback/')
def callback():
	#gets the code in url if user has given permissions
    code = request.args.get('code')
    if code:
    	#uses code acquired to get user's access_token
		access_token = api.exchange_code_for_access_token(code)[0]

		if access_token:
			#saves access_token to be used later
		    session['access_token'] = access_token
		    return redirect("/")

		else:
		    return "Code missing. Please try again."
    else:
        return "Please give permissions to continue."

#handling exceptions/errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def inter_error(e):
    return render_template("500.html"), 500


@app.route("/contact/")
def contact():
    return render_template("contact.html")


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/User_Recent_Media/")
def User_Recent_Media():
    u = InstagramAPI(access_token=session['access_token'], client_secret=secret.secrets['client_secret'])
    recent_media, next_ = u.user_recent_media()
    photos_thumbnail = []
    photos_standard = []
    for media in recent_media:
        photos_thumbnail.append("%s" % media.images['thumbnail'].url)
        photos_standard.append("%s" % media.images['standard_resolution'].url)
    return render_template("recent.html",thumb=photos_thumbnail,photos=photos_standard)


@app.route("/User_Media_Feed/")
def User_Media_Feed():
    u = InstagramAPI(access_token=session['access_token'], client_secret=secret.secrets['client_secret'])
    media_feed, next_ = u.user_media_feed()
    photos_thumbnail = []
    photos_standard = []
    while next_:
        for media in media_feed:
            photos_thumbnail.append("%s" % media.images['thumbnail'].url)
            photos_standard.append("%s" % media.images['standard_resolution'].url)
        media_feed, next_ = u.user_media_feed(with_next_url=next_)
    return render_template("recent.html",thumb=photos_thumbnail,photos=photos_standard)


@app.route("/Location_Recent_Media/")
def Location_Recent_Media():
    return "Location_Recent_Media function()"


@app.route("/Media_Search/")
def Media_Search():
    return "Media_Search function()"


@app.route("/Popular_Media/")
def Popular_Media():
    return "Popular_Media function()"


@app.route("/User_Search/")
def User_Search():
    return "User_Search function()"


@app.route("/User_Follows/")
def User_Follows():
    return "User_Follows function()"


@app.route("/Location_Search/")
def Location_Search():
    return "Location_Search function()"


@app.route("/Tags/")
def Tags():
    return "Tags function()"

# Running the app

if (__name__)=="__main__":
	app.run()
