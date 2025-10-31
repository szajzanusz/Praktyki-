import sys
import os
import argparse
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import urllib.parse

# --- Ustawienia ogólne ---
BANNER_W, BANNER_H = 1200, 900
HEADER_RATIO = 0.28  # procent wysokości przeznaczony na nagłówek


# --- Funkcje pomocnicze ---
def search_pixabay(api_key, query, per_page=20):
    """Wyszukuje zdjęcia na Pixabay."""
    q = urllib.parse.quote_plus(query)
    url = f"https://pixabay.com/api/?key={api_key}&q={q}&image_type=photo&per_page={per_page}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json().get("hits", [])


def download_image(url):
    """Pobiera obraz z danego URL."""
    resp = requests.get(url, stream=True, timeout=15)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")


def fit_and_crop(im, target_w, target_h):
    """Dopasowuje zdjęcie (cover) i przycina do wymiarów."""
    iw, ih = im.size
    scale = max(target_w / iw, target_h / ih)
    new_size = (int(iw * scale) + 1, int(ih * scale) + 1)
    im2 = im.resize(new_size, Image.LANCZOS)
    left = (im2.width - target_w) // 2
    top = (im2.height - target_h) // 2
    return im2.crop((left, top, left + target_w, top + target_h))


def make_banner(img1, img2, text, out_prefix="banner"):
    """Tworzy baner ze zdjęciami i tekstem."""
    bg_color = (random.randint(30, 255), random.randint(30, 255), random.randint(30, 255))

    banner = Image.new("RGB", (BANNER_W, BANNER_H), color=bg_color)
    draw = ImageDraw.Draw(banner)
    header_h = int(BANNER_H * HEADER_RATIO)

    # --- Duża czcionka Arial 68 ---
    try:
        font = ImageFont.truetype("C:\\USERS\\SZAJZANUSZ\\APPDATA\\LOCAL\\MICROSOFT\\WINDOWS\\FONTS\\OSWALD-REGULAR.TTF", size=58)
    except Exception:
        print("⚠️ Uwaga: Nie znaleziono czcionki Arial, używam domyślnej.")
        font = ImageFont.load_default()

    # --- Pozycjonowanie tekstu ---
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=6)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    text_x = (BANNER_W - text_w) // 2
    text_y = (header_h - text_h) // 2

    draw.multiline_text(
        (text_x, text_y),
        text,
        fill=(0, 0, 0),
        font=font,
        spacing=6,
        align="center"
    )

    # --- Zdjęcia ---
    target_h = BANNER_H - header_h
    left_img = fit_and_crop(img1, BANNER_W // 2, target_h)
    right_img = fit_and_crop(img2, BANNER_W - BANNER_W // 2, target_h)

    banner.paste(left_img, (0, header_h))
    banner.paste(right_img, (BANNER_W // 2, header_h))

    # --- Zapis ---
    out_jpg = f"{out_prefix}.jpg"
    out_png = f"{out_prefix}_source.png"
    banner.save(out_jpg, quality=90)
    banner.save(out_png)
    return out_jpg, out_png





def choose_two_hits(hits):
    """Losowo wybiera dwa różne zdjęcia z wyników."""
    if not hits:
        raise RuntimeError("Brak wyników wyszukiwania.")
    if len(hits) == 1:
        return hits[0], hits[0]
    return random.sample(hits, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="Pixabay API key", required=True)
    parser.add_argument("--q", help="keywords (comma-separated) lub lokalne ścieżki do plików", required=True)
    parser.add_argument("--text", help="nagłówek", required=True)
    parser.add_argument("--out", default="banner")
    args = parser.parse_args()

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

    out_jpg, out_png = make_banner(images[0], images[1], args.text, out_prefix=args.out)
    print("✅ Gotowe pliki:", out_jpg, "oraz", out_png)


if __name__ == "__main__":
    main()
