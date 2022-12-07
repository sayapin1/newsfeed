from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pymysql


app = Flask(__name__)
db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90!', charset='utf8')

@app.route('/')
def main():
    if "user_id" in session:
        print(session["user_id"])
        return render_template("main.html", username = session.get("user_id"))
    else:
        return render_template('login.html')

@app.route('/register')
def join():
    return render_template('register.html')
    

@app.route('/register', methods=["post"])
def register():
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90!', charset='utf8')
    cursor = db.cursor()
    cursor.execute("USE newsfeed;")
    cursor.execute('select * from users;')

    
    user_id = request.form["user_id"]
    user_pw = request.form["user_pw"]
    user_pw = request.form["name"]

    cursor.execute("INSERT INTO users (user_id, user_pw) VALUES(%s,%s)", (user_id, user_pw,))

    db.commit()
    db.close()

    return redirect(url_for("main"))


@app.route('/login', methods=["GET"])
def login():
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90!', charset='utf8')
    user_id = request.args.get("user_id")
    user_pw = request.args.get("user_pw")

    cursor = db.cursor()
    if cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id)):
        rows = cursor.fetchone()
        print(rows)
        print(rows[2])
        db.close()

        if user_pw == rows[3]:
            print("3")
            session['user_id'] = rows[2]
            print(session['user_id'])
            return redirect(url_for("main")) #로그인성공 알럿?
        else:
            return redirect(url_for("main")) #비밀번호 다름
    else:
        db.close()
        return redirect(url_for("main")) #없는 아이디

@app.route('/logout')
def logout():
    session.pop("user_id")
    return redirect(url_for("main"))


@app.route('/user', methods=['POST'])
def insert_user():
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90', charset='utf8')
    cursor = db.cursor()

    cursor.execute("USE newsfeed;")

    cursor.execute('select * from users;')


    name = request.form['name_give']
    intro = request.form['intro_give']
    picture = request.form['picture_give']


    sql = """insert into users (name, intro, picture)
         values (%s,%s,%s)
        """
    cursor.execute(sql, (name, intro, picture))

    db.commit()
    db.close()
    return 'insert success', 200

@app.route('/mypage/<id>', methods=['GET'])
def show_user(id):
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90', charset='utf8')
    print(id)
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("USE newsfeed;")
    cursor.execute('select * from users;')

    sql = f"SELECT * FROM users where id = {id}"
    f"update post set title "
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(rows)
    mypage = {
        "name": rows[0]["name"],
        "intro": rows[0]["intro"]
        # "picture": rows[0]["picture"]
    }
    print(mypage)
    db.commit()
    db.close()

    return jsonify({"mypage": mypage})

@app.route("/post/get", methods=["GET"])
def get_post():
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90', charset='utf8')
    curs = db.cursor()

    sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name
    from post p inner join category c on p.category_name = c.category_name 
    inner JOIN users u ON p.user_id = u.user_id"""

    curs.execute(sql)
    post_list = curs.fetchall()
    db.commit()
    db.close()

    doc = []
    for post in post_list:
        pos = {"number": post[0],
               "title": post[1],
               "content": post[2],
               "created_at": post[3],
               "category": post[4],
               "name": post[5]}

        doc.append(pos)
    return jsonify({"posts": doc})

@app.route("/category/<id>", methods=["GET"])
def category(id):
    return render_template('category.html')

@app.route("/category/get/<id>", methods=["GET"])
def get_category(id):
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90!', charset='utf8')
    curs = db.cursor()
    sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name
    from post p inner join category c on p.category_name = c.category_name 
    inner JOIN users u ON p.user_id = u.user_id
    where c.id = %s""" %(id)

    curs.execute(sql)
    post_list = curs.fetchall()
    print(post_list)
    db.close()

    doc = []
    for post in post_list:
        pos = {"number": post[0],
               "title": post[1],
               "content": post[2],
               "created_at": post[3],
               "category": post[4],
               "name": post[5]}

        doc.append(pos)
    return jsonify({"posts": doc})

@app.route("/post/<id>", methods=["GET"])
def show_post(id):
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90', charset='utf8')
    curs = db.cursor()
    sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name
        from post p inner join category c on p.category_name = c.category_name 
        inner JOIN users u ON p.user_id = u.user_id
        where p.id=%s""" %(id)

    curs.execute(sql)
    post = curs.fetchall()
    db.close()

    return render_template('post.html', post=post[0])


@app.route("/post/create", methods=["GET", "POST"])
def create_post():
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90', charset='utf8')
    curs = db.cursor()
    if request.method == "GET":
        return render_template('write.html')

    else:
        name = request.form['name_give']
        user_id = request.form['user_id_give']
        user_pw = request.form['user_pw_give']
        title = request.form['title_give']
        content = request.form['content_give']
        category_name = request.form['cat_name_give']

        sql = """insert into users values (null, '%s', '%s', '%s',null, null)""" % (name, user_id, user_pw)
        curs.execute(sql)
        curs.fetchall()
        db.commit()

        sql = """insert into post values (null, '%s', '%s', default , '%s', '%s')""" % (
        title, content, user_id, category_name)
        curs.execute(sql)
        curs.fetchall()
        db.commit()
        db.close()

        return jsonify({'msg': '등록완료!'})


@app.route("/post/up/<id>", methods=["GET", "POST"])
def post_up(id):
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90', charset='utf8')
    curs = db.cursor()
    # post_id = request.form['id_give']
    if request.method == "GET":
        sql = """select p.title, p.content, p.category_name from post p WHERE p.id = %s""" %(id)
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
    db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='Wjstnqls90', charset='utf8')
    curs = db.cursor()
    id = request.form['del_give']
    sql = """delete from post where id = '%s'""" % (id)

    curs.execute(sql)
    curs.fetchall()
    db.commit()
    db.close()

    return jsonify({'msg': '삭제완료!'})



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='127.0.0.1', port=8000, debug=True)