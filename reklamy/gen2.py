import sys
import os
import argparse
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import urllib.parse

# --- Ustawienia ---
BANNER_W, BANNER_H = 1200, 900
HEADER_RATIO = 0.28

# --- Funkcje pomocnicze ---
def search_pixabay(api_key, query, per_page=20):
    q = urllib.parse.quote_plus(query)
    url = f"https://pixabay.com/api/?key={api_key}&q={q}&image_type=photo&per_page={per_page}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json().get("hits", [])

def download_image(url):
    resp = requests.get(url, stream=True, timeout=15)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")

def fit_and_crop(im, target_w, target_h):
    iw, ih = im.size
    scale = max(target_w / iw, target_h / ih)
    new_size = (int(iw*scale)+1, int(ih*scale)+1)
    im2 = im.resize(new_size, Image.LANCZOS)
    left = (im2.width - target_w)//2
    top = (im2.height - target_h)//2
    return im2.crop((left, top, left+target_w, top+target_h))

def choose_two_hits(hits):
    if not hits:
        raise RuntimeError("Brak wyników wyszukiwania.")
    if len(hits) == 1:
        return hits[0], hits[0]
    return random.sample(hits, 2)

# --- Placeholder Banner ---
def make_placeholder_banner(out_prefix="banner"):
    width, height = 1024, 768
    header_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    placeholder_color = (200,200,200)
    border_color = (100,100,100)
    layout = random.choice(['top', 'bottom', 'left', 'right'])
    print(f"Układ nagłówka: {layout}")

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    margin = 20

    if layout == 'top':
        header_height = int(height*0.25)
        draw.rectangle([0,0,width,header_height], fill=header_color)
        placeholder_width = (width - 3*margin)//2
        placeholder_height = height - header_height - 2*margin
        y = header_height + margin
        left_box = [margin, y, margin+placeholder_width, y+placeholder_height]
        right_box = [2*margin+placeholder_width, y, 2*margin+2*placeholder_width, y+placeholder_height]

    elif layout == 'bottom':
        header_height = int(height*0.25)
        draw.rectangle([0,height-header_height,width,height], fill=header_color)
        placeholder_width = (width - 3*margin)//2
        placeholder_height = height - header_height - 2*margin
        y = margin
        left_box = [margin, y, margin+placeholder_width, y+placeholder_height]
        right_box = [2*margin+placeholder_width, y, 2*margin+2*placeholder_width, y+placeholder_height]

    elif layout == 'left':
        header_width = int(width*0.25)
        draw.rectangle([0,0,header_width,height], fill=header_color)
        placeholder_width = width - header_width - 3*margin
        placeholder_height = (height - 3*margin)//2
        x = header_width + margin
        top_box = [x, margin, x+placeholder_width, margin+placeholder_height]
        bottom_box = [x, 2*margin+placeholder_height, x+placeholder_width, 2*margin+2*placeholder_height]
        left_box, right_box = top_box, bottom_box

    else: # right
        header_width = int(width*0.25)
        draw.rectangle([width-header_width,0,width,height], fill=header_color)
        placeholder_width = width - header_width - 3*margin
        placeholder_height = (height - 3*margin)//2
        x = margin
        top_box = [x, margin, x+placeholder_width, margin+placeholder_height]
        bottom_box = [x, 2*margin+placeholder_height, x+placeholder_width, 2*margin+2*placeholder_height]
        left_box, right_box = top_box, bottom_box

    draw.rectangle(left_box, fill=placeholder_color, outline=border_color, width=3)
    draw.rectangle(right_box, fill=placeholder_color, outline=border_color, width=3)

    out_file = f"{out_prefix}.png"
    img.save(out_file)
    print("Obraz zapisany jako", out_file)
    return out_file

# --- Banner z obrazkami i losowym układem ---
def make_banner(img1, img2, text, bg="gray", out_prefix="banner"):
    if bg == "yellow":
        bg_color = (random.randint(1,255), random.randint(1,255), random.randint(1,255))
    else:
        bg_color = (240,242,244)
    banner = Image.new("RGB", (BANNER_W, BANNER_H), bg_color)
    draw = ImageDraw.Draw(banner)

    layout = random.choice(['top','bottom'])
    print(f"Układ nagłówka: {layout}")
    margin = 20

    try:
        font_main = ImageFont.truetype("C:\\Windows\\Fonts\\impact.ttf", size=50)
    except:
        font_main = ImageFont.load_default()

    if layout in ['top','bottom']:
        header_h = int(BANNER_H*HEADER_RATIO)
        target_h = BANNER_H - header_h
        left_img = fit_and_crop(img1, BANNER_W//2 - margin, target_h - margin)
        right_img = fit_and_crop(img2, BANNER_W - BANNER_W//2 - margin, target_h - margin)

        if layout == 'top':
            draw.rectangle([0,0,BANNER_W,header_h], fill=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            banner.paste(left_img, (0, header_h))
            banner.paste(right_img, (BANNER_W//2, header_h))
            bbox = draw.multiline_textbbox((0,0), text, font=font_main, spacing=6)
            draw.multiline_text(((BANNER_W-(bbox[2]-bbox[0]))//2, (header_h-(bbox[3]-bbox[1]))//2), text, fill=(0,0,0), font=font_main, spacing=6, align="center")
        else:
            draw.rectangle([0,BANNER_H-header_h,BANNER_W,BANNER_H], fill=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            banner.paste(left_img, (0,0))
            banner.paste(right_img, (BANNER_W//2,0))
            bbox = draw.multiline_textbbox((0,0), text, font=font_main, spacing=6)
            draw.multiline_text(((BANNER_W-(bbox[2]-bbox[0]))//2, BANNER_H-header_h + (header_h-(bbox[3]-bbox[1]))//2), text, fill=(0,0,0), font=font_main, spacing=6, align="center")

    else:  # left/right
        header_w = int(BANNER_W*HEADER_RATIO)
        target_w = BANNER_W - header_w
        target_h = BANNER_H//2 - margin
        top_img = fit_and_crop(img1, target_w - margin, target_h - margin)
        bottom_img = fit_and_crop(img2, target_w - margin, target_h - margin)

        if layout == 'left':
            draw.rectangle([0,0,header_w,BANNER_H], fill=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            banner.paste(top_img, (header_w,0))
            banner.paste(bottom_img, (header_w,BANNER_H//2))
            bbox = draw.multiline_textbbox((0,0), text, font=font_main, spacing=6)
            draw.multiline_text(((header_w-(bbox[2]-bbox[0]))//2,(BANNER_H-(bbox[3]-bbox[1]))//2), text, fill=(0,0,0), font=font_main, spacing=6, align="center")
        else:
            draw.rectangle([BANNER_W-header_w,0,BANNER_W,BANNER_H], fill=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            banner.paste(top_img, (0,0))
            banner.paste(bottom_img, (0,BANNER_H//2))
            bbox = draw.multiline_textbbox((0,0), text, font=font_main, spacing=6)
            draw.multiline_text((BANNER_W-header_w + (header_w-(bbox[2]-bbox[0]))//2,(BANNER_H-(bbox[3]-bbox[1]))//2), text, fill=(0,0,0), font=font_main, spacing=6, align="center")

    out_jpg = f"{out_prefix}.jpg"
    out_png = f"{out_prefix}_source.png"
    banner.save(out_jpg, quality=90)
    banner.save(out_png)
    return out_jpg, out_png

# --- Main ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="Pixabay API key")
    parser.add_argument("--q", help="keywords (comma-separated) lub lokalne pliki")
    parser.add_argument("--text", help="nagłówek")
    parser.add_argument("--bg", choices=["gray","yellow"], default="gray")
    parser.add_argument("--out", default="banner")
    parser.add_argument("--placeholder", action="store_true", help="Tworzy banner placeholder")
    args = parser.parse_args()

    if args.placeholder:
        make_placeholder_banner(args.out)
        return

    if not args.key or not args.q or not args.text:
        print("❌ Podaj --key, --q i --text lub użyj --placeholder")
        sys.exit(1)

    parts = [p.strip() for p in args.q.split(",") if p.strip()]
    local_paths = [p for p in parts if os.path.isfile(p)]
    images = []

    if len(local_paths) >= 2:
        for p in local_paths[:2]:
            images.append(Image.open(p).convert("RGB"))
    else:
        query = ",".join(parts)
        print("🔍 Wyszukiwanie w Pixabay:", query)
        hits = search_pixabay(args.key, query, per_page=50)
        if not hits:
            print("❌ Brak wyników dla zapytania:", query)
            sys.exit(1)
        a_hit, b_hit = choose_two_hits(hits)
        url1 = a_hit.get("largeImageURL") or a_hit.get("webformatURL")
        url2 = b_hit.get("largeImageURL") or b_hit.get("webformatURL")
        print("📸 Pobrane URL:\n", url1, "\n", url2)
        images.append(download_image(url1))
        images.append(download_image(url2))

    out_jpg, out_png = make_banner(images[0], images[1], args.text, bg=args.bg, out_prefix=args.out)
    print("✅ Gotowe pliki:", out_jpg, "oraz", out_png)

if __name__ == "__main__":
    main()
