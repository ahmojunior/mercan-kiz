# Mercan Kız

Mercan Kız masalı için karakter görselleri, sahneler ve tanıtım siteleri.

## İçerik

| Klasör / dosya | Ne |
|---|---|
| `site/`, `site2/` | Statik tanıtım sitesinin iki tasarımı (`index.html` + `img/`) |
| `yazdir/film-seridi.html` | Yazdırılabilir film şeridi (PDF çıktısı: `Mercan Kız - Film Şeridi.pdf`) |
| `Sahneler/` | Kaynak sahne görselleri |
| `*.png` (kökte) | Karakter şemaları (kaynak) |
| `tools/kes.py` | Şemalardan şeffaf arka planlı WebP kesitleri üretir |

## Çalıştırma

Siteler derleme gerektirmez:

```bash
python3 -m http.server 8000 --directory site2
```

Görselleri yeniden üretmek için (Pillow, numpy, scipy gerekir):

```bash
python3 -I tools/kes.py site2/img
```
