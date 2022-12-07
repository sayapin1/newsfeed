from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pymysql


app = Flask(__name__)
db = pymysql.connect(host='localhost', user='root', db='newsfeed', password='0114', charset='utf8')


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        cursor = db.cursor()

        cursor.execute("USE newsfeed;")

        cursor.execute('select * from users;')

        user_id = request.form['user_id']
        user_pw = request.form['user_pw']

        cursor.execute("INSERT INTO users (user_id, user_pw) VALUES(%s,%s)", (user_id, user_pw))

        db.commit()
        db.close()

        return redirect(url_for("login"))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        user_id = request.form['user_id']
        user_pw = request.form['user_pw']
        print("1")
        cursor = db.cursor()
        if cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id)):

            rows = cursor.fetchone()
            print(rows)
            print(rows[2])
            db.commit()
            db.close()

            if user_pw == rows[2]:
                print("3")
                session['user_id'] = rows[1]
                print(session['user_id'])
                return render_template("main.html")
            else:
                return "Error password or user not match"
        else:
            return render_template("login.html")
@app.route('/user', methods=['POST'])
def insert_user():
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



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='127.0.0.1', port=8000, debug=True)

