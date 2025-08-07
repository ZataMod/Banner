from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from io import BytesIO
from urllib.request import urlopen
from flask import Response

def handler(request):
    # Đọc query từ URL
    params = request.args
    name = params.get("name", "Zata Mod")
    avatar_url = params.get("avatar", "")
    
    # Tạo banner
    banner_width = 1600
    banner_height = 500
    avatar_size = 300
    border_thickness = 8

    banner = Image.new("RGB", (banner_width, banner_height), "#0f172a")
    draw = ImageDraw.Draw(banner)

    # Load avatar
    try:
        avatar = Image.open(urlopen(avatar_url)).convert("RGB")
    except:
        avatar = Image.open("avatar.jpg").convert("RGB")  # fallback

    avatar = avatar.resize((avatar_size, avatar_size), Image.LANCZOS)
    mask = Image.new("L", (avatar_size, avatar_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
    avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    avatar.putalpha(mask)

    # Thêm viền trắng
    bordered_avatar = Image.new("RGBA", (avatar_size + 2 * border_thickness, avatar_size + 2 * border_thickness), (255, 255, 255, 0))
    bordered_mask = Image.new("L", bordered_avatar.size, 0)
    bordered_draw = ImageDraw.Draw(bordered_mask)
    bordered_draw.ellipse((0, 0, bordered_avatar.size[0], bordered_avatar.size[1]), fill=255)
    bordered_avatar.putalpha(bordered_mask)
    bordered_avatar.paste(avatar, (border_thickness, border_thickness), avatar)

    avatar_x = 80
    avatar_y = (banner_height - bordered_avatar.height) // 2
    banner.paste(bordered_avatar, (avatar_x, avatar_y), bordered_avatar)

    # Kẻ line
    line_x = avatar_x + bordered_avatar.width + 40
    draw.line([(line_x, 60), (line_x, banner_height - 60)], fill=(255, 255, 255, 80), width=3)

    # Text
    try:
        font = ImageFont.truetype("SVN-VT Redzone Classic.otf", 80)
    except:
        font = ImageFont.load_default()

    lines = [
        "-- Member Join Group --",
        name,
        "Vừa Tham Gia Nhóm"
    ]

    y = 100
    for text in lines:
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        draw.text((line_x + 40, y), text, font=font, fill="white")
        y += 90

    # Kết quả trả về ảnh
    output = BytesIO()
    banner.save(output, format='PNG')
    output.seek(0)

    return Response(output.read(), mimetype="image/png")
