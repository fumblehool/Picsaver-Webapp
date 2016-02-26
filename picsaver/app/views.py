from flask import render_template, request, redirect, session
from instagram.client import InstagramAPI
from app import app
from config import secrets
from dbconnect import connection

api = InstagramAPI(**secrets)


@app.route("/")
def main():
    if "access_token" in session:
        u = InstagramAPI(access_token=session['access_token'],
                         client_secret=secrets['client_secret'])
        user = u.user()
        c, conn = connection()
        x = c.execute("SELECT * FROM user WHERE username = '{0}'".format(user))

        if int(x) == 0:
            c.execute("INSERT INTO user VALUES({0},{1})"
                      .format(session['access_token'], user))
            conn.commit()
            c.close()
            conn.close()
        return render_template("call.html", title=user.username,
                               full_name=user.full_name)
    else:
        return render_template("index.html")


@app.route('/connect/')
def connect():
    url = api.get_authorize_url(scope=["likes", "comments"])
    return redirect(url)


@app.route('/instagram_callback/')
def callback():
    code = request.args.get('code')
    if code:
        access_token = api.exchange_code_for_access_token(code)[0]

        if access_token:
            session['access_token'] = access_token
            return redirect("/")
        else:
            return "Code missing. Please try again."
    else:
        return "Please give permissions to continue."


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


@app.route("/User_Recent_Media/<int:page>/")
@app.route("/User_Recent_Media/1")
def User_Recent_Media(page=1):
    u = InstagramAPI(access_token=session['access_token'],
                     client_secret=secrets['client_secret'])
    recent_media, next_ = u.user_recent_media()
    for i in range(1, page):
        recent_media, next_ = u.user_recent_media(count=20,
                                                  with_next_url=next_)
    photos_thumbnail = []
    photos_standard = []
    title = "User Recent Media-Page " + str(page)
    prev_page = False
    next_page = False
    if next_:
        prev_page = True
    if page != 1:
        next_page = True
    for media in recent_media:
        photos_thumbnail.append("%s" % media.images['thumbnail'].url)
        photos_standard.append("%s" % media.images['standard_resolution'].url)
    return render_template("recent.html", thumb=photos_thumbnail,
                           photos=photos_standard, prev=prev_page,
                           next=next_page, page=page, title=title)


@app.route("/User_Media_Feed/<int:page>/")
@app.route("/User_Media_Feed/1")
def User_Media_Feed(page=1):
    u = InstagramAPI(access_token=session['access_token'],
                     client_secret=secrets['client_secret'])
    media_feed, next_ = u.user_media_feed(count=20)
    for i in range(1, page):
        media_feed, next_ = u.user_media_feed(count=20, with_next_url=next_)
    photos_thumbnail = []
    photos_standard = []
    title = "User Media Feed-Page " + str(page)
    prev_page = False
    next_page = False
    if next_:
        prev_page = True
    if page != 1:
        next_page = True
    for media in media_feed:
        photos_thumbnail.append("%s" % media.images['thumbnail'].url)
        photos_standard.append("%s" % media.images['standard_resolution'].url)
    return render_template("recent.html", thumb=photos_thumbnail,
                           photos=photos_standard, prev=prev_page,
                           next=next_page, page=page, title=title)


@app.route("/User_Liked_Media/<int:page>/")
@app.route("/User_Liked_Media/1")
def User_Liked_Media(page=1):
    u = InstagramAPI(access_token=session['access_token'],
                     client_secret=secrets['client_secret'])
    liked_media, next_ = u.user_liked_media()
    for i in range(1, page):
        liked_media, next_ = u.user_liked_media(count=20, with_next_url=next_)
    photos_thumbnail = []
    photos_standard = []
    title = "User Liked Media-Page " + str(page)
    prev_page = False
    next_page = False
    if next_:
        prev_page = True
    if page != 1:
        next_page = True
    for media in liked_media:
        photos_thumbnail.append("%s" % media.images['thumbnail'].url)
        photos_standard.append("%s" % media.images['standard_resolution'].url)
    return render_template("recent.html", thumb=photos_thumbnail,
                           photos=photos_standard, prev=prev_page,
                           next=next_page, page=page, title=title)


@app.route("/Location_Recent_Media/")
def Location_Recent_Media():
    return "Location_Recent_Media function()"


@app.route("/Media_Search/", methods=['GET', 'POST'])
def Media_Search():
    if request.method == "POST":
        query = request.form['query']
        u = InstagramAPI(access_token=session['access_token'])
        media_search, next_ = u.media_search(query)
        # return str(media_search)
    return render_template("media_search.html", title="Media Search")


@app.route("/Popular_Media/")
def Popular_Media():
    u = InstagramAPI(access_token=session['access_token'],
                     client_secret=secrets['client_secret'])
    popular_media = u.media_popular()
    photos_thumbnail = []
    photos_standard = []
    title = "Popular Media-Page "
    for media in popular_media:
        photos_thumbnail.append("%s" % media.images['thumbnail'].url)
        photos_standard.append("%s" % media.images['standard_resolution'].url)
    return render_template("recent.html", thumb=photos_thumbnail,
                           photos=photos_standard, title=title)


@app.route("/User_Search/", methods=['GET', 'POST'])
def User_Search():
    u = InstagramAPI(access_token=session['access_token'],
                     client_secret=secrets['client_secret'])
    if request.method == "POST":
        query = request.form['query']
        if query is None:
            return "Please Enter something."
        else:
            user_search_result = u.user_search(query)
            users = []
            user_profile_picture = []
            for user in user_search_result:
                users.append("{}".format(user.username))
                user_profile_picture.append("{}".format(user.profile_picture))
            return render_template("search.html", title="User Search",
                                   users=users,
                                   user_profile_picture=user_profile_picture,
                                   len=len(users))
    return render_template("search.html", title="User Search")


@app.route("/User_Follows/<int:page>/")
@app.route("/User_Follows/1")
def User_Follows(page=1):
    u = InstagramAPI(access_token=session['access_token'],
                     client_secret=secrets['client_secret'])
    user_follows, next_ = u.user_follows()
    for i in range(1, page):
        user_follows, next_ = u.user_follows(with_next_url=next_)
    follows = []
    title = "User Follows-Page " + str(page)
    prev_page = False
    next_page = False
    if next_:
        prev_page = True
    if page != 1:
        next_page = True
    for link in user_follows:
        follows.append("{0}".format(link.username))
    return render_template("recent.html", follows=follows,
                           prev=prev_page, next=next_page,
                           page=page, title=title)


@app.route("/User_Followed_By/1")
@app.route("/User_Followed_By/<int:page>/")
def User_Followed_By(page=1):
    u = InstagramAPI(access_token=session['access_token'],
                     client_secret=secrets['client_secret'])
    user_followed_by, next_ = u.user_followed_by(client_secret=secrets
                                                 ['client_secret'])
    for i in range(1, page):
        user_followed_by, next_ = u.user_followed_by(with_next_url=next_)
    follows = []
    profile_images = []
    title = "User Followed By-Page " + str(page)
    prev_page = False
    next_page = False
    if next_:
        prev_page = True
    if page != 1:
        next_page = True
    for link in user_followed_by:
        follows.append("{0}".format(link.username))
        profile_images.append("{0}".format(link.profile_picture))
    return render_template("recent.html", follows=follows,
                           profile_images=profile_images, prev=prev_page,
                           next=next_page, page=page, title=title)


@app.route("/Location_Search/")
def Location_Search():
    return "Location_Search function()"


@app.route("/Tags/")
def Tags():
    return "Tags function()"
