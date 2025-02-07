from flask import Flask, render_template, request, send_file
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    barcode_image = None
    barcode_data = None
    
    if request.method == "POST":
        barcode_data = request.form["product_info"]

        # ตรวจสอบว่าเป็นตัวเลขทั้งหมดและมีความยาว 13 หลัก
        if not barcode_data.isdigit():
            return "Error: Barcode must contain only numbers for EAN-13 format!", 400
        
        if len(barcode_data) != 13:
            return "Error: EAN-13 barcode must be exactly 13 digits long!", 400
        
        if barcode_data:
            try:
                # ใช้ EAN-13 หากข้อมูลเป็นตัวเลข 13 หลัก
                barcode_instance = barcode.get_barcode_class('ean13')
                barcode_image = barcode_instance(barcode_data, writer=ImageWriter())

                # บันทึกบาร์โค้ดลงใน BytesIO เพื่อให้สามารถส่งกลับเป็นไฟล์
                img_stream = BytesIO()
                barcode_image.write(img_stream)
                img_stream.seek(0)

                return send_file(img_stream, mimetype='image/png', as_attachment=True, download_name='barcode.png')
            except Exception as e:
                return f"Error: {str(e)}", 500

    return render_template("index.html", barcode_data=barcode_data, barcode_image=barcode_image)

if __name__ == "__main__":
    app.run(debug=True)
