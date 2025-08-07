from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

@app.route("/api/banner")
def banner():
    name = request.args.get("name", "Tên người dùng")
    avatar_url = request.args.get("avatar")

    if not avatar_url:
        return "Thiếu ?avatar=...", 400

    try:
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        return f"Lỗi tải avatar: {e}", 400

    # Tạo banner
    banner_width = 800
    banner_height = 200
    avatar_size = 150
    border_thickness = 5

    banner = Image.new("RGB", (banner_width, banner_height), color=(30, 30, 30))
    avatar = avatar.resize((avatar_size, avatar_size))

    mask = Image.new("L", (avatar_size, avatar_size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)

    bordered_avatar = Image.new("RGBA", (avatar_size + border_thickness*2, avatar_size + border_thickness*2), (255, 255, 255, 0))
    draw_border = ImageDraw.Draw(bordered_avatar)
    draw_border.ellipse((0, 0, avatar_size + border_thickness*2, avatar_size + border_thickness*2), fill=(255, 255, 255, 255))
    bordered_avatar.paste(avatar, (border_thickness, border_thickness), mask=mask)

    banner.paste(bordered_avatar, (30, (banner_height - bordered_avatar.height) // 2), bordered_avatar)

    draw = ImageDraw.Draw(banner)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    text_position = (avatar_size + 60, (banner_height - 40) // 2)
    draw.text(text_position, name, font=font, fill=(255, 255, 255))

    # Xuất ra ảnh
    output = BytesIO()
    banner.save(output, format='PNG')
    output.seek(0)

    return send_file(output, mimetype='image/png')

# Handler cho Vercel
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
