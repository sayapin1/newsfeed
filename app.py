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
    return render_template('index.html')

@app.route("/write", methods=["GET"])
def createpage():
    return render_template('write.html')




@app.route("/post/get", methods=["GET"])
def get_post():
    sql = """select p.id, p.title, p.content, p.created_at, c.category_name, u.name
    from post p inner join category c on p.category_name = c.category_name 
    inner JOIN users u ON p.user_id = u.user_id"""

    curs.execute(sql)
    post_list = curs.fetchall()
    db.commit()
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

@app.route("/post/create", methods=["POST"])
def create_post():
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

    sql = """insert into post values (null, '%s', '%s', default , '%s', '%s')""" %(title, content, user_id, category_name)
    curs.execute(sql)
    curs.fetchall()
    db.commit()

    return jsonify({'msg':'등록완료!'})

@app.route("/post/update/<id>", methods=["GET"])
def updatepage(id):
    return render_template('update.html')

@app.route("/post/up/<id>", methods=["POST"])
def post_up(id):
    # post_id = request.form['id_give']
    title = request.form['title_give']
    content = request.form['content_give']
    category_name = request.form['cat_name_give']

    # sql = """update post set title = '%s', content = '%s', category_name = '%s'  where id ='%s'""" %(title, content, category_name, id)
    sql =
    curs.execute(sql)
    curs.fetchall()
    db.commit()

    return jsonify({'msg': '수정완료'})

@app.route("/post/del", methods=["Delete"])
def post_del():
    id = request.form['del_give']
    sql = """delete from post where id = '%s'""" %(id)

    curs.execute(sql)
    curs.fetchall()
    db.commit()

    return jsonify({'msg':'삭제완료!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)