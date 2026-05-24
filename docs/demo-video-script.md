# Demo Video Konuşma Metni
## Car Rental Cloud — Cloud Computing Proje Sunumu

**Tahmini süre:** ~5–6 dakika  
**Dil:** Türkçe

---

## 🎬 GİRİŞ (0:00 – 0:30)

> *Ekranı aç, canlı siteyi göster: https://web-production-707f1.up.railway.app*

"Merhaba. Bu videoda Cloud Computing dersi kapsamında geliştirdiğim **Car Rental Cloud** projesini tanıtacağım.

Proje, 12-Factor App metodolojisini tam olarak uygulayan, bulut tabanlı bir araç kiralama yönetim sistemidir. Uygulama Python ve Flask ile yazılmış, PostgreSQL ve Redis ile desteklenmiş, Docker ile konteynerize edilmiş ve **Railway** bulut platformuna deploy edilmiştir.

Şu anda gördüğünüz ekran, Railway üzerinde canlı olarak çalışan uygulamanın kendisi."

---

## 📊 DASHBOARD TURU (0:30 – 1:15)

> *Sayfanın üst kısmını göster — stat kartları, status dot*

"Üst kısımda üç özet kart görüyoruz:
- **Available cars:** Şu an kiralanabilir araç sayısı
- **Active rentals:** Devam eden kiralama sayısı
- **Fleet revenue:** Tamamlanan ve devam eden kiralamalardan elde edilen toplam gelir

Sağ üstte yeşil nokta görüyorsunuz — bu uygulamanın `/readyz` endpoint'ine yapılan gerçek zamanlı bir sağlık kontrolü. Yeşil yanıyorsa uygulama tam olarak hazır demektir; veritabanı ve cache bağlantıları dahil.

Karanlık tema tamamen CSS custom properties ile yazılmış, mobil uyumlu bir tasarım."

---

## 🚗 ARAÇ EKLEME (1:15 – 2:00)

> *"Add car" formunu aç, doldur*

"Şimdi sisteme yeni bir araç ekleyelim."

> *Forma şunları yaz:*
> - Plate: `34-TEST-01`
> - Make: `Toyota`
> - Model: `Corolla`
> - Year: `2024`
> - Location: `Ankara`
> - Daily Rate: `1500`

"Plaka, marka, model, yıl, konum ve günlük ücret giriyoruz. Save car diyorum…

Araç eklendi. Sol taraftaki fleet listesine baktığımızda yeni aracın **yeşil** renkte göründüğünü görüyoruz — bu 'available' statüsü. Kiralandığında **turuncu**, bakımdayken **kırmızı** oluyor. Bu renkler CSS ile anlık olarak yönetiliyor."

---

## 👤 MÜŞTERİ EKLEME (2:00 – 2:30)

> *"Add customer" formunu aç*

"Şimdi bir müşteri kaydedelim."

> *Forma şunları yaz:*
> - Full name: `Ali Yilmaz`
> - Email: `ali@example.com`
> - Phone: `+90 532 000 0000`

"Ad, e-posta ve telefon numarasını giriyorum. Save customer…

Müşteri kaydedildi. E-posta adresi veritabanında unique constraint ile korunuyor — aynı e-posta iki kez girilemez."

---

## 📋 KİRALAMA OLUŞTURMA (2:30 – 3:15)

> *"New rental" formuna geç*

"Şimdi kiralama işlemi yapalım. Az önce eklediğimiz araç ve müşteri drop-down menülerde otomatik görünüyor."

> *Araç ve müşteriyi seç, tarihler otomatik dolu gelir*

"Araç, müşteri ve tarih aralığını seçiyorum. Create rental…

Kiralama oluşturuldu. Toplam fiyat **otomatik hesaplandı** — gün sayısı çarpı günlük ücret. Bu hesaplama tamamen sunucu tarafında yapılıyor, client'a güvenilmiyor.

Ayrıca aynı araç için tarih çakışması varsa sistem HTTP 400 hatası veriyor ve kiralama reddediliyor. Bu iş kuralı servis katmanında uygulanıyor."

---

## ↩ KİRALAMA İADESİ (3:15 – 3:40)

> *Rentals tablosunda aktif kiralama satırına git*

"Kiralama tablosunda az önce oluşturduğumuz kaydı görüyoruz, statüsü **active**. Return butonuna tıklıyorum…

İşlem tamamlandı. Kiralama statüsü **completed** oldu, araç otomatik olarak **available** statüsüne döndü. Bu iki işlem veritabanında atomik olarak gerçekleşiyor."

---

## 📈 METRİKLER (3:40 – 4:10)

> *Sayfayı aşağı kaydır, Live Metrics paneline git, Refresh'e tıkla*

"Sayfanın altında **Live Metrics** paneli var. Refresh tuşuna basıyorum…

Bu veriler `/metrics` endpoint'inden geliyor. Bu endpoint Prometheus formatında metrik üretiyor — araç ve kiralama sayılarını statüslerine göre gösteriyor. Barların animasyonu saf CSS ile yapılmış.

Gerçek bir üretim ortamında bu endpoint Prometheus veya Grafana'ya bağlanarak tam monitoring altyapısı kurulabilir."

---

## 🔄 CI/CD PIPELINE (4:10 – 4:45)

> *Tarayıcıda GitHub Actions sayfasını aç: github.com/batuhan-zeytun/car-rental-cloud/actions*

"Şimdi CI/CD pipeline'ına bakalım. Her `main` branch'ine push yapıldığında bu pipeline otomatik çalışıyor.

Üç aşama var:
1. **test** — Python 3.12 ile pytest çalıştırılıyor, in-memory SQLite kullanılıyor
2. **docker-build** — Docker image git SHA ile taglenip build ediliyor
3. **deploy** — Railway otomatik deploy ediyor, ardından `/healthz` endpoint'i kontrol edilerek canlıya geçiş doğrulanıyor

Üç aşama da yeşil — production'a kod, testleri geçmeden ulaşamıyor."

---

## ☁️ RAILWAY DASHBOARD (4:45 – 5:15)

> *Railway dashboard'unu aç: railway.app*

"Railway dashboard'una geçiyorum. Projede üç servis çalışıyor:

- **web** — Flask/Gunicorn Docker container
- **Postgres** — Railway tarafından yönetilen PostgreSQL 16
- **Redis** — Railway tarafından yönetilen Redis 7

Tüm ortam değişkenleri — `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY` — burada güvenli şekilde saklanıyor. Kaynak kodda tek bir şifre veya bağlantı adresi yok. Bu 12-Factor'ın üçüncü faktörü olan **Config** faktörünü karşılıyor."

---

## ⚙️ FLASK CLI — FACTOR XII (5:15 – 5:45)

> *Terminali aç, proje klasörüne git*

"Son olarak 12-Factor'ın on ikinci faktörü olan **Admin Processes**'i göstereyim. Yönetimsel görevler, uygulamayla aynı ortamda çalışan tek seferlik süreçler olarak implemente edilmeli."

```bash
flask stats
```

> *Komutu çalıştır, çıktıyı göster*

"Gördüğünüz gibi `flask stats` komutu, uygulamanın bağlandığı aynı `DATABASE_URL` üzerinden anlık istatistikleri terminale yazdırıyor. Bunun yanı sıra `flask init-db`, `flask seed-db` ve `flask drop-db` komutları da mevcut.

Bu komutlar Railway'in CLI'ı üzerinden `railway run flask stats` şeklinde uzaktan da çalıştırılabiliyor."

---

## 🏁 KAPANIŞ (5:45 – 6:00)

"Bu projede 12-Factor App metodolojisinin tüm on iki faktörü uygulandı:
tek codebase, bağımlılık yönetimi, config'in environment variable'larda saklanması, backing services, build/release/run ayrımı, stateless processes, port binding, concurrency, disposability, dev/prod parity, structured logging ve admin processes.

Canlı uygulama ve kaynak kodun linkleri raporda mevcut. İzlediğiniz için teşekkürler."

---

## 📝 HAZIRLIK NOTLARI

- Videodan önce siteyi bir kez aç, verilerin yüklendiğinden emin ol
- Terminal için `flask stats` çalıştırmadan önce `cd` ile proje klasörüne gir ve `set FLASK_APP=wsgi` yap
- GitHub Actions ve Railway sekmeleri baştan açık olsun, videoyu durdurma gerek kalmasın
- Kayıt için Windows'ta **Win+G** (Xbox Game Bar) veya OBS kullanabilirsin
- Ekran kaydı bittikten sonra YouTube'a yükle, linki rapordaki `*(link to be added)*` kısmına ekle
