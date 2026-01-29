from sqlalchemy import text

from app import db
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    profile = db.Column(db.String(255))


def getAllUserList():
    sql = text("""SELECT * FROM user""")
    result = db.session.execute(sql)
    return [dict(row._mapping) for row in result]


# ==========================
# GET USER BY ID
# ==========================
def getUserById(user_id: int):
    sql = text("""SELECT *FROM user WHERE id = :user_id""")
    result = db.session.execute(
        sql,
        {"user_id": user_id}
    ).fetchone()

    return dict(result._mapping) if result else None