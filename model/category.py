from app import db
from sqlalchemy import text


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)


# Fetch all categories as dicts
def getAllCategoryList():
    sql = text("SELECT * FROM category ORDER BY name ASC")
    result = db.session.execute(sql)
    return [dict(row._mapping) for row in result]


# Fetch single category by ID
def getCategoryById(category_id):
    return Category.query.get(category_id)
