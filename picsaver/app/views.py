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
        x = c.execute("SELECT * FROM user WHERE access_token = '{0}'".format(str(session['access_token'])))
        session['id'] = user.id
        session['username'] = user.username
        if int(x) == 0:
            c.execute("INSERT INTO user VALUES('{0}','{1}','{2}')".format(session['access_token'],user.username,user.full_name))
            conn.commit()
            c.close()
            conn.close()
        return render_template("call.html", title=user.username,
                               full_name=user.full_name,
                               profile_picture=user.profile_picture,
                               counts=user.counts)
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


@app.route("/contact/", methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form['name']
        comment = request.form['comment']
        if not name or not comment:
            e = "Please fill fields."
            return render_template("contact.html", error=e)
        else:
            return render_template("contact.html", error=e)
    return render_template("contact.html")


@app.route("/logout/")
def logout():
    session.clear()
    return redirect("/")


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
        photos_thumbnail.append("{}".format(media.images['thumbnail'].url))
        photos_standard.append("{}".format(media.images['standard_resolution']
                               .url))
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
        photos_thumbnail.append("{}".format(media.images['thumbnail'].url))
        photos_standard.append("{}".format(media.images['standard_resolution']
                               .url))
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
        photos_thumbnail.append("{}".format(media.images['thumbnail'].url))
        photos_standard.append("{}".format(media.images['standard_resolution']
                               .url))
    return render_template("recent.html", thumb=photos_thumbnail,
                           photos=photos_standard, prev=prev_page,
                           next=next_page, page=page, title=title)


@app.route("/Location_Recent_Media/", methods=['GET', 'POST'])
def Location_Recent_Media():
    if request.method == "POST":
        lat = request.form['latitude']
        lng = request.form['longitude']
        u = InstagramAPI(access_token=session['access_token'])
        media_search = u.media_search(lat=lat, lng=lng, count=32)
        media = []
        for link in media_search:
            media.append("{}".format(link.get_thumbnail_url()))
        return render_template("media_search.html", media=media)
    return render_template("media_search.html", title="Location Recent Media")


@app.route("/Media_Search/", methods=['GET', 'POST'])
def Media_Search():
    if request.method == "POST":
        q = request.form['query']
        lat = request.form['latitude']
        lng = request.form['longitude']
        if not q or not lat or not lng:
            e = "Please Enter latitude and longitude"
            return render_template("media_search.html", title="Media Search",
                                   error=e)
        u = InstagramAPI(access_token=session['access_token'])
        media_search = u.media_search(query=q, lat=lat, lng=lng, count=32)
        media = []
        for link in media_search:
            media.append("{}".format(link.get_thumbnail_url()))
        return render_template("media_search.html", media=media)
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
            if len(users) is 0:
                e = "No Users Found!"
                return render_template("search.html", error=e,
                                       title="User Search")

            return render_template("search.html", title="User Search",
                                   users=users,
                                   user_profile_picture=user_profile_picture,
                                   )
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
    profile_images = []
    title = "User Follows-Page " + str(page)
    prev_page = False
    next_page = False
    if next_:
        prev_page = True
    if page != 1:
        next_page = True
    for link in user_follows:
        follows.append("{0}".format(link.username))
        profile_images.append("{0}".format(link.profile_picture))
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


@app.route("/Tag_Search/1", methods=['GET', 'POST'])
@app.route("/Tag_Search/<int:page>/", methods=['GET', 'POST'])
def Tag_Search(page=1):
    if request.method == "POST":
        query = request.form["query"]
        if not query:
            e = "Please Enter something."
            return render_template("search.html", error=e, title="Tag Search")
        u = InstagramAPI(access_token=session['access_token'],
                         client_secret=secrets['client_secret'])
        tag_search, next_tag = u.tag_search(q=query)
        tag_recent_media, next_ = u.tag_recent_media(tag_name=tag_search[0]
                                                     .name)
        for i in range(1, page):
            tag_recent_media, next_ = u.tag_recent_media(tag_name=tag_search[0]
                                                         .name,
                                                         with_next_url=next_)
        tags = []
        imgs = []
        title = "Tag Search-Page " + str(page)
        prev_page = False
        next_page = False
        if next_:
            prev_page = True
        if page != 1:
            next_page = True
#        for media in tag_recent_media:
#            tags.append("{}".format(media.get_thumbnail_url()))
#            tags.append("{}".format(media.get_standard_url()))
        return render_template("search.html", tags=tags, imgs=imgs,
                               prev=prev_page, next=next_page, page=page,
                               title=title)

    return render_template("search.html")


@app.route("/Tags/")
def Tags():
    return "Tags function()"


@app.route("/User/<path:username>/<int:page>/")
@app.route("/User/<path:username>/1/")
def user(username, page=1):
    u = InstagramAPI(access_token=session['access_token'],
                     client_secret=secret.secrets['client_secret'])
    id = u.user_search(username)[0].id
    user_media, next_ = u.user_recent_media(user_id=id,count=20)

    for i in range(1, page):
        user_media, next_ = u.user_recent_media(user_id=id,
                                                count=20,
                                                with_next_url=next_)
    photos_thumbnail = []
    photos_standard = []
    title = username + " Recent Media-Page " + str(page)
    prev_page = False
    next_page = False
    if next_:
        prev_page = True
    if page != 1:
        next_page = True
    for media in user_media:
        photos_thumbnail.append("%s" % media.images['thumbnail'].url)
        photos_standard.append("%s" % media.images['standard_resolution'].url)
    return render_template("recent.html", thumb=photos_thumbnail,
                           photos=photos_standard, prev=prev_page,
                           next=next_page, page=page, title=title)
