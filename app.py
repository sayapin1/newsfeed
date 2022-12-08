from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import timedelta
from flask_paginate import Pagination, get_page_args

import pymysql
from flask_bcrypt import Bcrypt

from datetime import datetime
import os


app = Flask(__name__)

db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')
Bcrypt = Bcrypt(app)

@app.route('/')
def main():
    if "user_id" in session:
        print(session["user_id"])
        return redirect(url_for("get_all_post"))
        # return render_template("main.html", username = session.get("user_id"))

    else:
        return render_template('login.html')


@app.route('/register')
def join():
    return render_template('register.html')


@app.route('/register', methods=["post"])
def register():
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')
    cursor = db.cursor()
    cursor.execute("USE newsfeed;")
    cursor.execute('select * from users;')

    user_id = request.form["user_id"]
    user_pw = request.form["user_pw"]
    name = request.form["name"]


    cursor.execute("INSERT INTO users (user_id, user_pw,name) VALUES(%s,%s,%s)", (user_id, 
    Bcrypt.generate_password_hash(user_pw), name))


    db.commit()
    db.close()

    return redirect(url_for("login"))

@app.route('/login', methods=["GET","POST"])
def login():

    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')
    cursor = db.cursor()
    cursor.execute("USE newsfeed;")
    cursor.execute('select * from users;')
    
    if request.method == "POST":
        user_id = request.form['user_id']
        password1 = request.form['user_pw']
        cursor = db.cursor()
        result = cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id))
        
        if result >0:
            user = cursor.fetchone()
            password = user[3]   
           
            if Bcrypt.check_password_hash(password,password1): #비번 암호화 전에 생성한 비번으로 로그인시 salt오류 발생
                # session['login'] =True
                session['user_id'] = user[2]
                session['user_pw'] = user[3]
                return redirect(url_for("main")) 
            
    db.close()
    return redirect(url_for("main"))
            
           

@app.route('/logout')
def logout():
    session.pop("user_id")
    return redirect(url_for("main"))


@app.route('/profile/up', methods=["GET", "POST"])
def profile_up():
    print("1")
    if request.method == "GET":
        db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (session["user_id"]))
        rows = cursor.fetchone()
        print(rows)
        db.commit()
        db.close()
        return render_template('profile_up.html', rows=rows)
    else:
        db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')

        cursor = db.cursor()
        cursor.execute('select * from users;')

        name = request.form['name']
        intro = request.form['intro']
        file = request.files['picture']

        if not os.path.isdir("static/upload/image"):
            os.makedirs('static/upload/image')  # upload/image 폴더 없을 경우 자동생성

        extension = file.filename.split('.')[-1]  # .스플릿으로 파일 확장자 가져오기
        today = datetime.now()
        mtime = today.strftime('%Y-%m-%d-%H-%M-%S')
        filename = f'{mtime}.{extension}'
        print(filename)
        save_to = f'static/upload/image/{filename}'
        file.save(save_to)


        cursor.execute("SELECT * FROM users WHERE user_id=%s", (session["user_id"]))

        sql ="""UPDATE newsfeed.users t SET t.name = '%s', t.intro = '%s', t.picture = '%s' WHERE t.user_id = '%s'""" %(name, intro, filename, session["user_id"])
        cursor.execute(sql)
        cursor.fetchall()
        db.commit()
        db.close()
        print("3")
        return redirect(url_for("myprofile"))


@app.route("/profile/<user_id>")
def profile(user_id):
    print(user_id)
    if user_id:
        num = user_id
        owner = user_id
        ses = session["user_id"]
        if owner == ses:
            check = True
        else:
            check = False
    else:
        num = session["user_id"]
        check = True
    print(check)

    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=%s", (num))

    rows = cursor.fetchone()
    print(rows)
    db.close()
    session["image"] = rows[4]
    return render_template('profile.html', rows=rows, check=check)

@app.route("/myprofile")
def myprofile():
    num = session["user_id"]

    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=%s", (num))

    rows = cursor.fetchone()
    print(rows)
    db.close()
    session["image"] = rows[4]
    print(session["image"])
    return render_template('profile.html', rows=rows, check=True)


@app.route("/post", methods=["GET"])
def get_all_post():
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')
    curs = db.cursor()

    per_page = 6
    page, _, offset = get_page_args(per_page=per_page)

    curs.execute("SELECT COUNT(*) FROM post;")
    all_count = curs.fetchall()[0][0]

    sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name, u.user_id
        from post p inner join category c on p.category_name = c.category_name 
        inner JOIN users u ON p.user_id = u.user_id ORDER BY 'created_at' DESC LIMIT %s OFFSET %s""" %(per_page, offset)

    curs.execute(sql)
    post_list = curs.fetchall()
    print(post_list)
    db.close()

    pagination = Pagination(page=page, per_page=per_page, total=all_count)

    return render_template('main.html', post_list=post_list, pagination=pagination)

# @app.route("/category/<id>", methods=["GET"])
# def category(id):
#     return render_template('category.html')
#
#
# @app.route("/category/get/<id>", methods=["GET"])
# def get_category(id):
#     db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')
#
#     curs = db.cursor()
#     sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name
#     from post p inner join category c on p.category_name = c.category_name
#     inner JOIN users u ON p.user_id = u.user_id
#     where c.id = %s""" % (id)
#
#     curs.execute(sql)
#     post_list = curs.fetchall()
#     print(post_list)
#     db.close()
#
#     doc = []
#     for post in post_list:
#         pos = {"number": post[0],
#                "title": post[1],
#                "content": post[2],
#                "created_at": post[3],
#                "category": post[4],
#                "name": post[5]}
#
#         doc.append(pos)
#     return jsonify({"posts": doc})


@app.route("/post/<id>", methods=["GET"])
def show_post(id):
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')

    curs = db.cursor()
    sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name, u.user_id
        from post p inner join category c on p.category_name = c.category_name 
        inner JOIN users u ON p.user_id = u.user_id
        where p.id=%s""" % (id)

    curs.execute(sql)
    post = curs.fetchall()
    db.close()

    return render_template('post.html', post=post[0])


@app.route("/post/create", methods=["GET", "POST"])
def create_post():
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')
    curs = db.cursor()

    if request.method == "GET":
        return render_template('write.html')

    else:

        # name = request.form['name_give']
        user_id = session.get("user_id")
        # user_pw = request.form['user_pw_give']
        title = request.form['title_give']
        content = request.form['content_give']
        category_name = request.form['cat_name_give']
        print(user_id)

        sql = """insert into post values (null, '%s', '%s', default , '%s', '%s')""" % (
        title, content, user_id, category_name)
        curs.execute(sql)
        curs.fetchall()
        db.commit()
        db.close()

        return jsonify({'msg': '등록완료!'})


@app.route("/up/<id>", methods=["GET", "POST"])
def post_up(id):
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')

    curs = db.cursor()
    # post_id = request.form['id_give']
    if request.method == "GET":
        sql = """select p.title, p.content, p.category_name from post p WHERE p.id = %s""" % (id)
        curs.execute(sql)
        data = curs.fetchall()
        db.close()

        return render_template('update.html', data=data[0])

    if request.method == "POST":
        title = request.form['title_give']
        content = request.form['content_give']
        category_name = request.form['cat_name_give']

        sql = """UPDATE newsfeed.post t SET t.title = '%s', t.content = '%s', t.category_name = '%s' WHERE t.id = %s""" % (
            title, content, category_name, id)
        curs.execute(sql)
        curs.fetchall()
        db.commit()
        db.close()

        return jsonify({'msg': '수정완료'})


@app.route("/post/del", methods=["Delete"])
def post_del():
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='spartapw', charset='utf8')

    curs = db.cursor()
    id = request.form['del_give']
    sql = """delete from post where id = '%s'""" % (id)

    curs.execute(sql)
    curs.fetchall()
    db.commit()
    db.close()

    return jsonify({'msg': '삭제완료!'})


app.secret_key = 'super secret key'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=5)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='127.0.0.1', port=8000, debug=True)
