
from PIL import Image, ImageDraw, ImageFont

from app import db
from sqlalchemy import text
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    category_id = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(128))
    description = db.Column(db.String(500), nullable=True)

def getAllProductList():
    sql = text("""
        SELECT p.*, c.name AS category
        FROM product AS p
        INNER JOIN category AS c ON p.category_id = c.id
    """)
    result = db.session.execute(sql)
    return [dict(row._mapping) for row in result]


def getProductById(product_id: int):
    sql = text("""
        SELECT p.*, c.name AS category
        FROM product AS p
        INNER JOIN category AS c ON p.category_id = c.id
        WHERE p.id = :product_id
    """)
    result = db.session.execute(
        sql,
        {"product_id": product_id}
    ).fetchone()

    return dict(result._mapping) if result else None

def add_watermark(image_path, text="Panha"):
    # Open the image and convert to RGBA
    image = Image.open(image_path).convert("RGBA")

    # Make a watermark layer
    watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)

    # Load a TTF font if available, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 30)  # font size 30
    except:
        font = ImageFont.load_default()

    # Get text width and height
    # Using textbbox to calculate the bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Bottom-right corner position with 10px margin
    x = image.width - text_width - 10
    y = image.height - text_height - 10

    # Draw the text in red with some transparency
    draw.text((x, y), text, fill=(255, 0, 0, 120), font=font)

    # Combine watermark with the original image
    watermarked = Image.alpha_composite(image, watermark)

    # Convert to RGB and save (overwrite original)
    watermarked.convert("RGB").save(image_path)


def getProductByCategory(category_id):
    return Product.query.filter_by(category_id=category_id).all()