# Karakter şemalarından şeffaf arka planlı WebP kesitler ve sahne görselleri üretir.
# Kullanım: python3 -I tools/kes.py <çıktı klasörü>
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

KOK = os.path.join(os.path.dirname(__file__), "..")
CIKTI = sys.argv[1]
os.makedirs(CIKTI, exist_ok=True)

S, B, M, Y = "Şehzade ve Genç Hükümdar", "Büyücü Kadın", "Mercan Kız", "Yaşlı Kadın"
# (kaynak, ad, x0, y0, x1, y1, hedef yükseklik)
KESITLER = [
    (S, "sehzade", 220, 124, 744, 1224, 600), (S, "sehzade-2", 736, 124, 1324, 1236, 340),
    (S, "sehzade-y1", 300, 1232, 552, 1516, 200), (S, "sehzade-y2", 584, 1232, 832, 1516, 200), (S, "sehzade-y3", 860, 1232, 1108, 1516, 200),
    (S, "hukumdar", 1532, 40, 1972, 1224, 600), (S, "hukumdar-2", 2112, 44, 2532, 1236, 340),
    (S, "hukumdar-y1", 1616, 1232, 1876, 1516, 200), (S, "hukumdar-y2", 1896, 1232, 2152, 1516, 200), (S, "hukumdar-y3", 2168, 1232, 2428, 1516, 200),
    (B, "buyucu", 720, 60, 1312, 1092, 600), (B, "buyucu-2", 1416, 64, 2032, 1092, 340),
    (B, "buyucu-y1", 740, 1100, 1136, 1512, 200), (B, "buyucu-y2", 1168, 1100, 1564, 1512, 200), (B, "buyucu-y3", 1586, 1100, 1990, 1512, 200),
    (M, "mercan", 876, 68, 1296, 1124, 600), (M, "mercan-2", 1460, 68, 1856, 1128, 340),
    (M, "mercan-y1", 816, 1140, 1144, 1524, 200), (M, "mercan-y2", 1200, 1140, 1528, 1524, 200), (M, "mercan-y3", 1584, 1140, 1912, 1524, 200),
    (Y, "yasli", 800, 64, 1304, 1056, 600), (Y, "yasli-2", 1432, 64, 1868, 1056, 340),
    (Y, "yasli-y1", 712, 1076, 1136, 1500, 200), (Y, "yasli-y2", 1156, 1076, 1576, 1508, 200), (Y, "yasli-y3", 1592, 1076, 2016, 1504, 200),
    # ejderha: şemadaki 1. ve 3. kafa neredeyse aynı, yalnızca 1 ve 2 kullanılıyor
    ("Ejderha", "ejderha", 364, 108, 1488, 980, 520), ("Ejderha", "ejderha-2", 1532, 96, 2404, 972, 300),
    ("Ejderha", "ejderha-y1", 672, 1012, 1028, 1480, 200), ("Ejderha", "ejderha-y2", 1188, 992, 1524, 1488, 200),
    ("At", "at", 80, 180, 1292, 1372, 520), ("At", "at-2", 1292, 176, 2050, 1388, 300), ("At", "at-y1", 2032, 648, 2664, 1376, 240),
]

def kes(kaynak, x0, y0, x1, y1, bosluk_ac):
    tam = np.asarray(Image.open(os.path.join(KOK, kaynak + ".png")).convert("RGB")).astype(np.float32)
    kagit = np.median(tam[::8, ::8].reshape(-1, 3), axis=0)  # kâğıt rengi
    c = tam[y0:y1, x0:x1]
    fark = np.abs(c - kagit).sum(axis=2)
    # siluet: belirgin boya + küçük boşlukları kapat + içi boş alanları (önlük, göz akı) doldur
    cekirdek = ndimage.binary_closing(fark > 28, structure=np.ones((5, 5)), iterations=1)
    lab, n = ndimage.label(cekirdek)
    if n:
        boy = ndimage.sum(cekirdek, lab, range(1, n + 1))
        cekirdek = np.isin(lab, 1 + np.nonzero(boy > 400)[0])
    # kapalı boşluklar doldurulur (önlük, göz akı); ejderha, at ve şehzadede (yay kirişi) düz kâğıt boşluklar (bacak arası) şeffaf kalır
    delikler, nd = ndimage.label(ndimage.binary_fill_holes(cekirdek) & ~cekirdek)
    siluet = cekirdek.copy()
    for i, sl in enumerate(ndimage.find_objects(delikler), 1):
        d = delikler[sl] == i
        if not bosluk_ac or d.sum() < 1500 or fark[sl][d].mean() > 14:
            siluet[sl] |= d
    yakin = ndimage.binary_dilation(siluet, iterations=6)
    yumusak = np.clip((fark - 14) / 36, 0, 1) * yakin  # sulu boya kenarları yarı saydam kalsın
    ic = ndimage.gaussian_filter(ndimage.binary_erosion(siluet, iterations=4).astype(np.float32), 1.2)
    a = np.maximum(yumusak, ic)
    # kenar piksellerindeki kâğıt rengini geri çıkar (açık hale kalmasın)
    aa = np.maximum(a, 1e-3)[..., None]
    rgb = np.clip((c - (1 - a[..., None]) * kagit) / aa, 0, 255)
    rgb = np.where(a[..., None] > 0.02, rgb, 0)
    return np.dstack([rgb, a * 255]).astype(np.uint8)

for kaynak, ad, x0, y0, x1, y1, h in KESITLER:
    im = Image.fromarray(kes(kaynak, x0, y0, x1, y1, kaynak in ("Ejderha", "At") or ad.startswith("sehzade-") or ad == "sehzade"), "RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    im = im.crop(bb)
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    a = np.asarray(im)[..., 3]
    assert a.max() == 255 and (a == 0).mean() > 0.2, ad  # opak figür + gerçek şeffaf arka plan
    im.save(os.path.join(CIKTI, ad + ".webp"), quality=84, method=6)

# sahneler: dosya oluşturulma sırası = taslaktaki kare sırası (görsel olarak kontrol edildi)
SAHNELER = ["uv5i06uv5i06uv5i", "lqtny4lqtny4lqtn", "r25nnor25nnor25n", "5ox6xe5ox6xe5ox6", "wcq3u0wcq3u0wcq3",
            "ywmietywmietywmi", "pqnnq1pqnnq1pqnn", "slhn3islhn3islhn", "158ger158ger158g", "556j0g556j0g556j"]
for i, kod in enumerate(SAHNELER, 1):
    im = Image.open(os.path.join(KOK, "Sahneler", f"Gemini_Generated_Image_{kod}.png")).convert("RGB")
    for w in (1600, 900):
        im.resize((w, round(w * im.height / im.width)), Image.LANCZOS).save(os.path.join(CIKTI, f"sahne-{i:02d}-{w}.webp"), quality=80, method=6)
print("tamam")
