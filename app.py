from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import style
import base64
from flask import Flask,render_template,request,redirect,flash,session,make_response
import math
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.secret_key='Anjali'

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///OneToMany.sqlite3"

db = SQLAlchemy(app) #which is same as db = SQLALchemy(app)

app.app_context().push()



@app.route("/",methods=['GET'])
def loginpage():
    return render_template("login.html")


@app.route("/admin",methods =["GET","POST"])
def Adminpage():
    return render_template("admin_login.html")



@app.route("/user",methods =["GET","POST"])
def Userpage():
    return render_template("user_login.html")

#-----------------sign in------------#
@app.route("/sign_up/user",methods = ["GET","POST"])
def sign():
    song = Songs.query.all()
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        addNew = User(username = username,email = email,password = password)
        db.session.add(addNew)
        db.session.commit()

        user =User.query.filter_by(username = username).first()
        play = Playlist.query.filter(Playlist.username == username).all()
        return render_template("home.html",user = user,song = song,play = play)

def AdminInfo():
    users = User.query.filter(User.role == 'User').all()
    creators = User.query.filter(User.role == 'Creator').all()
    genres = db.session.query(Album.genre).distinct().all()
    
    song = Songs.query.all()
    album = Album.query.all()
    l  = []
    al = []
    u  = []
    c  = []

    for gana in song:
        l.append(gana)
    for a in album:
        al.append(a)
    for user in users:
        u.append(user)
    for creator in creators:
        c.append(creator)

    total_songs = len(l)
    total_album=len(al)
    total_users = len(u)
    total_creator = len(c)
    total_genre = len(genres)
    return (total_album,total_songs,total_users,total_creator,song,total_genre,genres)

#-----------------Login--------------#
@app.route("/login/admin",methods = ["GET","POST"])
def login_admin():
    values = AdminInfo()
    
    distinct_genres = db.session.query(Album.genre).distinct().all()
    genres_list = [genre.genre for genre in distinct_genres]
    avg_list = []
    for genre in genres_list:
        avg = 0
        songs = db.session.query(Songs).join(Album).filter(Album.genre == genre).all()
        for song in songs:
            avg+=song.rating
        avg=avg/len(songs)
        avg =round(avg,1)
        avg_list.append(avg)

    style.use('ggplot')
    plt.figure(figsize=(7,5))
    plt.xlabel('Genres')
    plt.ylabel('avg_rating')
    plt.title("which genre songs are best")

    plt.bar(genres_list,avg_list,color='pink',width=0.5)
    
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.close()

    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
        
    if request.method=="POST":
        name = request.form['username']
        password = request.form['password']
        admin = User.query.filter_by(username = name).first()
        if admin.username == name and admin.password == password and admin.role == "admin":
            return render_template("admin.html",total_song = values[1],total_album = values[0],
                                   total_user = values[2],total_creator = values[3],song = values[4],
                                   total_genre=values[5],genres = values[6],image = image_base64)
        else:
            flash("admin name or Password is Incorrect, Please Try Again")
            return redirect("/admin")
        
    return render_template("admin.html",total_song = values[1],total_album = values[0],
                                   total_user = values[2],total_creator = values[3],song = values[4],
                                   total_genre=values[5],genres = values[6],image=image_base64)

@app.route("/login/user",methods = ["GET","POST"])
def login():
    song = Songs.query.all()
    if request.method=='POST':

        username = request.form['username']
        password = request.form['password']

        user =User.query.filter_by(username = username).first()
        if user == None:
            flash("User Not Found, Please SignUp To Continue.")
            return redirect("/user")
        elif user.username == username and user.password == password:
            session['logged_in'] = True
            session['username'] = username
            play = Playlist.query.filter(Playlist.username == username).all()
            return render_template("home.html",user = user,song = song,play = play)
        else:
            user = User.query.filter_by(username='default')
            flash("UserName or Password is Incorrect, Please Try Again")
            return redirect("/user")

@app.route("/admin_2",methods = ["GET","POST"])
def Admin_2():
    song = Songs.query.all()
    return render_template("admin2.html",song = song)
#---------------------LOGOUT-------------------------------#

@app.route("/logout",methods = ["GET","POST"])
def logout():
    session.pop('logged_in', None)
    return render_template("login.html")

#---------------------UserDashboard-----------------------------#
@app.route("/all_Songs",methods =["GET","POST"])
def user_Dashboard():
    song = Songs.query.all()
    username = session.get('username')
    user = User.query.filter_by(username = username).first()
    play = Playlist.query.filter(Playlist.username == username).all()
    return render_template("home.html",song=song,user = user,play = play)

#------------------creator register---------------------------#        
@app.route("/C_register",methods =["GET","POST"])
def C_Register():
    return render_template("creator_login.html")

#------------------Creator Dashboard----------------------#
def creator_info(username):
    user =User.query.filter_by(username = username).first()
    s = Songs.query.filter(Songs.user == user.id).all()
    a = Album.query.filter(Album.user == user.id).all()
    l=[]
    m = []
    avg = 0
    for gana in s:
        avg+=gana.rating
        l.append(gana)
    for album in a:
        m.append(album)

    avg=avg/len(l)
    avg =round(avg,2)
    total_songs = len(l)
    total_album=len(m)

    return (total_album,total_songs,s,avg,a)

@app.route("/role_Change",methods=["GET","POST"])
def Role_Change():
    if request.method == "POST":
        username = request.form['username']
        user =User.query.filter_by(username = username).first()
        new_role = request.form['role']
        if(user.role == "Creator"):
            values = creator_info(username)
            return render_template("Creator_Dashboard.html",user = user,
                                   total_songs = values[1],total_album=values[0],song = values[2],avg = values[3],album=values[4])
        else:
            user.role = new_role
            db.session.commit()
            return render_template("upload.html",user = user)
    
#------------------UploadSong-------------------------------#

@app.route("/upload/<int:id>",methods =["GET","POST"])
def uploadsongs(id):
    user =User.query.filter_by(id = id).first()
    if request.method == "POST":
        sname = request.form.get("sName").lower()
        lyrics = request.form.get("lyrics")
        date = request.form.get("date")
        exist_album_name = request.form.get("album_name").lower()
        exist_al_id = Album.query.filter_by(a_name = exist_album_name).first()
        aName = request.form.get("aName").lower()
        artist = request.form.get("artist").lower()
        genre = request.form.get("genre").lower()
        MP3 = request.files["songmp3"]
        songMP3 = base64.b64encode(MP3.read())

        if exist_album_name and aName:
            flash("Choose one either asign_album or new album")
            return render_template("upload.html",user=user)
        elif exist_album_name:
            toAdd = Songs(s_name = sname,lyrics = lyrics,date = date,album_id = exist_al_id.a_id,user =id,songMP3 = songMP3)
            db.session.add(toAdd)
            db.session.commit()
        elif aName:
            toadd = Album(a_name = aName,artist = artist,genre = genre,user = id)
            db.session.add(toadd)
            db.session.commit()
            new_a_id = Album.query.filter_by(a_name = aName).first()
            toAdd = Songs(s_name = sname,lyrics = lyrics,date = date,album_id = new_a_id.a_id,user =id,songMP3=songMP3)
            db.session.add(toAdd)
            db.session.commit()

        values = creator_info(user.username)
        return render_template("Creator_Dashboard.html",user = user,
                               total_songs = values[1],total_album=values[0],song = values[2],avg = values[3],album=values[4])
    return render_template("upload.html",user=user)
    
#-------------------upload_to_creatorDashboard--------------------------------#

@app.route("/my_dashboard/<int:id>",methods = ["GET","POST"])
def Creator_dashboard(id):
    user =User.query.filter_by(id = id).first()
    values = creator_info(user.username)
    return render_template("Creator_Dashboard.html",user = user,
                           total_songs = values[1],total_album=values[0],song = values[2],avg = values[3],album=values[4])

#---------------------all_about_playlist----------------------------#

@app.route("/playlist",methods =["GET","POST"])
def CreatePlayList():
    username = session.get('username')
    user = User.query.filter_by(username = username).first()
    song = Songs.query.all()
    if(request.method == "POST"):

        song_list = request.form.getlist("songname")#[1,2]
        p_name = request.form['p_name']

        song_ids = ','.join(map(str, song_list))
        #if a playlist already exist
        play_list = Playlist.query.filter_by(name = p_name).first()
        if play_list:
            if play_list.song_ids:
                play_list.song_ids += f",{song_ids}"
            else:
                play_list.song_ids = song_ids
            db.session.commit()
        else:
            p1 = Playlist(username = username,name = p_name,song_ids = song_ids)
            db.session.add(p1)
            db.session.commit()
            
        play = Playlist.query.filter(Playlist.username == username).all()
        return render_template("myProfile.html",play =play,user=user)
        
    
    return render_template("playlist.html",songs = song,user = user)

@app.route("/myplayList/<name>",methods = ['GET','POST'])
def MyplayList(name):
    play = Playlist.query.filter_by(name = name).first()
    song_ids = play.song_ids

    song_list = []
    for i in song_ids:
        if i!= ',':
            a = Songs.query.filter_by(s_id = i).first()
            song_list.append(a)
    
    return render_template("myPlayList.html",play=play,song_list=song_list)#,song=song)

#------------------Profile--------------------------------------#
@app.route("/my_profile",methods =["GET","POST"])
def profile():
    username = session.get('username')
    user = User.query.filter_by(username = username).first()
    play = Playlist.query.filter(Playlist.username == username).all()
    return render_template("myProfile.html",user= user,play=play)


#-----------------Lyrics_page---------------------------------------#
@app.route("/lyrics/<int:s_id>")
def Lyrics(s_id):
    
    song = Songs.query.filter_by(s_id = s_id).first()
    star = "⭐"*math.floor((song.rating))
    album = Album.query.filter_by(a_id = song.album_id).first()
    return render_template("lyrics.html",song = song,album=album,star = star)

@app.route("/play_song/<int:song_id>")
def playSong(song_id):
    song = Songs.query.filter_by(s_id = song_id).first()
    if song:
        audio_data = base64.b64decode(song.songMP3)
        response = make_response(audio_data)
        response.headers['Content-Type'] = 'audio/mpeg'
        return response
    else:
        return "Song not found",404

#-------------------Delete/Update/Add by creator--------------------------#
#DELETE-SONG--------------------------
@app.route("/c_delete/<int:s_id>")
def Delete_by_creator(s_id):
    s = Songs.query.filter_by(s_id = s_id).first()
    user = User.query.filter_by(id = s.user).first()
    song = Songs.query.get(s_id)

    playlists_with_song = Playlist.query.filter(Playlist.song_ids.contains(str(s_id))).all()

    if song:
        db.session.delete(song)
        for playlist in playlists_with_song:
            song_ids = playlist.song_ids.split(',')  # Split the string to a list
            song_ids = [int(id) for id in song_ids if int(id) != s_id]  # Remove the deleted song ID
            playlist.song_ids = ','.join(map(str, song_ids))  # Update the song IDs in the playlist
            db.session.add(playlist)
        db.session.commit()

        flash("deleted successfully.")
        values = creator_info(user.username)
        return render_template("Creator_Dashboard.html",user = user,
                                   total_songs = values[1],total_album=values[0],song = values[2],avg = values[3],album=values[4])
    else:
        flash("song is not available.")
        values = creator_info(user.username)
        return render_template("Creator_Dashboard.html",user = user,
                                   total_songs = values[1],total_album=values[0],song = values[2],avg = values[3],album=values[4])
#DELETE-ALBUM--------------------------
@app.route("/c_a_delete/<int:a_id>")
def DeleteAlbum(a_id):
    
    album = Album.query.filter_by(a_id =a_id).first()
    song =Songs.query.filter(Songs.album_id==a_id).all()
    user = User.query.filter_by(id = album.user ).first()
    if song:
        for s in song:
            db.session.delete(s)
    db.session.delete(album)
    db.session.commit()
    flash("deleted successfully.")
    values = creator_info(user.username)
    return render_template("Creator_Dashboard.html",user = user,
                                   total_songs = values[1],total_album=values[0],song = values[2],avg = values[3],album=values[4])
#EDIT---------------------------------------------------------------  
@app.route("/c_edit/<int:s_id>",methods = ['GET','POST'])
def Edit(s_id):
    song = Songs.query.filter_by(s_id=s_id).first()
    a = Album.query.filter_by(a_id = song.album_id).first()
    user = User.query.filter_by(id = song.user).first()
    if request.method=="POST":
        song.s_name = request.form.get("sName")
        song.lyrics = request.form.get("lyrics")
        song.date = request.form.get("date")
        a.a_id = request.form.get("album_id")
        a.a_name = request.form.get("aName")
        a.artist = request.form.get("artist")
        a.genre = request.form.get("genre")
        MP3 = request.files["songmp3"]
        songMP3 = base64.b64encode(MP3.read())
        song.songMP3=songMP3
        db.session.commit()
        values = creator_info(user.username)
        flash("deleted successfully.")
        return render_template("Creator_Dashboard.html",user = user,
                               total_songs = values[1],total_album=values[0],song = values[2],avg = values[3],album=values[4])


    return render_template("edit_song.html",song=song,album=a)
#--------------------------------------DELETE_BY_ADMIN-----------------------------------#
@app.route("/admin_delete/<int:s_id>")
def Delete_by_admin(s_id):
    s = Songs.query.filter_by(s_id = s_id).first()
    user = User.query.filter_by(id = s.user).first()
    song = Songs.query.get(s_id)

    playlists_with_song = Playlist.query.filter(Playlist.song_ids.contains(str(s_id))).all()

    db.session.delete(song)

    for playlist in playlists_with_song:
        song_ids = playlist.song_ids.split(',')  # Split the string to a list
        song_ids = [int(id) for id in song_ids if int(id) != s_id]  # Remove the deleted song ID
        playlist.song_ids = ','.join(map(str, song_ids))  # Update the song IDs in the playlist
        db.session.add(playlist)
    db.session.commit()

    flash("deleted successfully.")
    return redirect("/admin_2")

#------------------------delete_playlist------------------------#
@app.route("/delete_playlist/<int:id>")
def PlayListDelete(id):
    playlist = Playlist.query.filter_by(id=id).first()
    db.session.delete(playlist)
    db.session.commit()
    flash("deleted successfully.")
    return redirect("/my_profile")

#---------------------------rating------------------------------#
@app.route("/rate/<int:s_id>/<int:rating>",methods=['GET','POST'])
def Rating(s_id,rating):
    username = session.get('username')
    user = User.query.filter_by(username = username).first()
    song = Songs.query.filter_by(s_id=s_id).first()
    album = Album.query.filter_by(a_id = song.album_id).first()

    toadd = Rating(s_id = s_id,u_id = user.id,rating = rating)
    db.session.add(toadd)
    db.session.commit()

    ratings = Rating.query.filter_by(s_id=s_id).all()
    sum = 0
    count = 0
    for r in ratings:
        sum+= r.rating
        count+=1
    
    avg_rating = sum/count
    avg_rating = round(avg_rating,2)
    song.rating = avg_rating
    db.session.commit()
    star = "⭐"*math.floor((song.rating))
    return render_template("lyrics.html",song=song,album=album,star = star)

#--------------------------Search---------------------------------#
@app.route("/search",methods=['GET','POST'])
def Search():
    if request.method=="POST":
        name = request.form.get("search")
        name = name.lower()
        s =Songs.query.filter_by(s_name = name).first()
        a = Album.query.filter_by(artist = name).first()
        if s!= None and s:
            return render_template("search.html",s = s)
        elif a!= None and a:
            songs = db.session.query(Songs).join(Album).filter(Album.artist == name).all()
            return render_template("search.html",l=songs)
        else:
            flash(" No song/artist available")
            return redirect("/all_Songs")
            
        



#---------------------------All_about_Models-----------------------#
class Album(db.Model):
    a_id = db.Column(db.Integer, primary_key = True)
    a_name = db.Column(db.String(30), nullable = False)
    artist = db.Column(db.String(30), nullable = False)
    genre = db.Column(db.String(30), nullable = False)
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    songs = db.relationship("Songs", backref = "company")
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), default="User")  # Default role is "User"
    album = db.relationship("Album",backref = "album")
    song = db.relationship("Songs",backref = "User")

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable = False)
    name = db.Column(db.String(100),nullable = False)
    song_ids = db.Column(db.String)

class Songs(db.Model):
    s_id = db.Column(db.Integer, primary_key = True)
    s_name = db.Column(db.String(30), nullable = False)
    lyrics = db.Column(db.Text,nullable = False)
    date = db.Column(db.Integer,nullable = False)
    rating = db.Column(db.Integer,default=0)
    songMP3 = db.Column(db.BLOB)
    rate = db.relationship("Rating",backref = "song")
    album_id = db.Column(db.Integer, db.ForeignKey("album.a_id"))
    user = db.Column(db.Integer, db.ForeignKey("user.id"))

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer,nullable = False)
    rating = db.Column(db.Integer,default=0)
    s_id = db.Column(db.Integer, db.ForeignKey("songs.s_id"))


    

    



if __name__ == '__main__':
    app.debug=True
    app.run()
