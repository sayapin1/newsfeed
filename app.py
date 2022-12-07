from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

import pymysql

# 디비 연결하기
db = pymysql.connect(host="localhost",
                     port=3306,
                     user="root",
                     db='newsfeed',
                     password='spartapw',
                     charset='utf8')

curs = db.cursor()


@app.route("/", methods=["GET"])
def home():
    return render_template('main.html')


@app.route("/post/get", methods=["GET"])
def get_post():
    sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name
    from post p inner join category c on p.category_name = c.category_name 
    inner JOIN users u ON p.user_id = u.user_id"""

    curs.execute(sql)
    post_list = curs.fetchall()
    db.commit()

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
    sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name
    from post p inner join category c on p.category_name = c.category_name 
    inner JOIN users u ON p.user_id = u.user_id
    where c.id = %s""" %(id)

    curs.execute(sql)
    post_list = curs.fetchall()
    print(post_list)

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
    sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name
        from post p inner join category c on p.category_name = c.category_name 
        inner JOIN users u ON p.user_id = u.user_id
        where p.id=%s""" %(id)

    curs.execute(sql)
    post = curs.fetchall()

    return render_template('post.html', post=post[0])


# @app.route("/write", methods=["GET"])
# def createpage():
#     return render_template('write.html')

@app.route("/post/create", methods=["GET", "POST"])
def create_post():
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

        return jsonify({'msg': '등록완료!'})


@app.route("/post/up/<id>", methods=["GET", "POST"])
def post_up(id):
    # post_id = request.form['id_give']
    if request.method == "GET":
        sql = """select p.title, p.content, p.category_name from post p WHERE p.id = %s""" %(id)
        curs.execute(sql)
        data = curs.fetchall()

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

        return jsonify({'msg': '수정완료'})


@app.route("/post/del", methods=["Delete"])
def post_del():
    id = request.form['del_give']
    sql = """delete from post where id = '%s'""" % (id)

    curs.execute(sql)
    curs.fetchall()
    db.commit()

    return jsonify({'msg': '삭제완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


 # doc = []
        # for content in pre_update:
        #     a = {"title":content[0],
        #         "content": content[1],
        #         "category": content[2]}
        #
        #     doc.append(a)