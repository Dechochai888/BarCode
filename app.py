from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ตั้งค่าฐานข้อมูล SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# สร้างตารางสินค้า
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

# ฟังก์ชันสร้างฐานข้อมูล
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        barcode_data = request.form["product_info"]
        product_name = request.form["product_name"]

        if not barcode_data.isdigit() or len(barcode_data) != 13:
            return "Error: EAN-13 barcode must be exactly 13 digits!", 400

        # ตรวจสอบว่ามีอยู่ในฐานข้อมูลหรือยัง
        existing_product = Product.query.filter_by(barcode=barcode_data).first()
        if existing_product:
            return "Error: This barcode already exists in the database!", 400

        # บันทึกลงฐานข้อมูล
        new_product = Product(barcode=barcode_data, name=product_name)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    products = Product.query.all()
    return render_template("dashboard.html", products=products)

@app.route("/update/<int:product_id>", methods=["POST"])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    new_name = request.form["product_name"]

    product.name = new_name
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/delete/<int:product_id>")
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/generate/<barcode_data>")
def generate_barcode(barcode_data):
    if not barcode_data.isdigit() or len(barcode_data) != 13:
        return "Invalid barcode format!", 400

    barcode_instance = barcode.get_barcode_class('ean13')
    barcode_image = barcode_instance(barcode_data, writer=ImageWriter())

    img_stream = BytesIO()
    barcode_image.write(img_stream)
    img_stream.seek(0)

    return send_file(img_stream, mimetype='image/png', as_attachment=True, download_name='barcode.png')

@app.route("/api/products")
def api_get_products():
    products = Product.query.all()
    product_list = [{"id": p.id, "barcode": p.barcode, "name": p.name} for p in products]
    return jsonify(product_list)

if __name__ == "__main__":
    app.run(debug=True)
