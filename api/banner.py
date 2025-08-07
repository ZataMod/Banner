from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

def handler(request):
    from flask import Flask, request as flask_request, send_file
    app = Flask(__name__)

    @app.route("/")
    def create_banner():
        name = flask_request.args.get("name", "Tên người dùng")
        avatar_url = flask_request.args.get("avatar")
        font_path = "SVN-VT Redzone Classic.otf"

        if not avatar_url:
            return "Thiếu ?avatar=...", 400

        try:
            response = requests.get(avatar_url)
            avatar = Image.open(BytesIO(response.content)).convert("RGBA")
        except Exception as e:
            return f"Lỗi tải avatar: {e}", 400

        # --- Bắt đầu tạo banner ---
        banner_width = 1600
        banner_height = 500
        avatar_size = 300
        border_thickness = 8

        banner = Image.new("RGB", (banner_width, banner_height), "#0f172a")
        draw = ImageDraw.Draw(banner)

        avatar = avatar.resize((avatar_size, avatar_size))

        mask = Image.new("L", (avatar_size, avatar_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)

        bordered_avatar = Image.new("RGBA", (avatar_size + border_thickness*2, avatar_size + border_thickness*2), (255, 255, 255, 0))
        draw_border = ImageDraw.Draw(bordered_avatar)
        draw_border.ellipse((0, 0, avatar_size + border_thickness*2, avatar_size + border_thickness*2), fill=(255, 255, 255, 255))
        bordered_avatar.paste(avatar, (border_thickness, border_thickness), mask=mask)

        avatar_x = 80
        avatar_y = (banner_height - bordered_avatar.height) // 2
        banner.paste(bordered_avatar, (avatar_x, avatar_y), bordered_avatar)

        line_x = avatar_x + bordered_avatar.width + 40
        draw.line([(line_x, 120), (line_x, banner_height - 60)], fill=(255, 255, 255, 80), width=3)

        try:
            font = ImageFont.truetype(font_path, 70)
        except:
            font = ImageFont.load_default()

        lines = [
            "-- Member Join Group --",
            name,
            "Vừa tham gia nhóm"
        ]

        line_spacing = 15
        total_text_height = len(lines) * (font.size + line_spacing)
        text_y_start = (banner_height - total_text_height) // 2

        for i, line in enumerate(lines):
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            text_x = line_x + 40 + (banner_width - line_x - 80 - line_width) // 2
            text_y = text_y_start + i * (font.size + line_spacing)
            draw.text((text_x, text_y), line, font=font, fill=(255, 255, 255))

        # Trả ảnh
        output = BytesIO()
        banner.save(output, format='PNG')
        output.seek(0)
        return send_file(output, mimetype="image/png")

    return app(request.environ, lambda status, headers: None)
