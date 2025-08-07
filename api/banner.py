from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from urllib.request import urlopen
import os

def handler(request):
    name = request.args.get("name", "Người dùng")
    avatar_url = request.args.get("avatar", "")
    font_path = "SVN-VT Redzone Classic.otf"

    # Dòng chữ giống code gốc
    lines = [
        "-- Member Join Group --",
        name,
        "Vừa tham gia nhóm"
    ]

    # Kích thước banner
    banner_width = 1600
    banner_height = 500
    avatar_size = 300
    border_thickness = 8

    # Tạo nền
    banner = Image.new("RGB", (banner_width, banner_height), "#0f172a")
    draw = ImageDraw.Draw(banner)

    # Mở avatar từ URL
    try:
        with urlopen(avatar_url) as response:
            avatar = Image.open(BytesIO(response.read())).convert("RGBA")
    except:
        avatar = Image.new("RGBA", (avatar_size, avatar_size), (120, 120, 120, 255))  # fallback

    avatar = avatar.resize((avatar_size, avatar_size))

    # Mặt nạ hình tròn
    mask = Image.new("L", (avatar_size, avatar_size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)

    # Viền trắng
    bordered_avatar = Image.new("RGBA", (avatar_size + border_thickness*2, avatar_size + border_thickness*2), (255, 255, 255, 0))
    draw_border = ImageDraw.Draw(bordered_avatar)
    draw_border.ellipse((0, 0, avatar_size + border_thickness*2, avatar_size + border_thickness*2), fill=(255, 255, 255, 255))
    bordered_avatar.paste(avatar, (border_thickness, border_thickness), mask=mask)

    # Vị trí avatar
    avatar_x = 80
    avatar_y = (banner_height - bordered_avatar.height) // 2
    banner.paste(bordered_avatar, (avatar_x, avatar_y), bordered_avatar)

    # Line phân cách
    line_x = avatar_x + bordered_avatar.width + 40
    draw.line([(line_x, 120), (line_x, banner_height - 60)], fill=(255, 255, 255, 80), width=3)

    # Font
    try:
        font = ImageFont.truetype(font_path, 70)
    except:
        font = ImageFont.load_default()

    # Căn giữa chữ
    line_spacing = 15
    total_text_height = len(lines) * (font.size + line_spacing)
    text_y_start = (banner_height - total_text_height) // 2

    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        text_x = line_x + 40 + (banner_width - line_x - 80 - line_width) // 2
        text_y = text_y_start + i * (font.size + line_spacing)
        draw.text((text_x, text_y), line, font=font, fill=(255, 255, 255))

    # Xuất ảnh ra memory
    output = BytesIO()
    banner.save(output, format="PNG")
    output.seek(0)

    # Trả ảnh về HTTP response
    from flask import Response
    return Response(output.read(), mimetype='image/png')
