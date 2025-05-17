# Proje Kurulum Kılavuzu

Bu proje için sanal ortam kurulumu ve gerekli paketlerin yüklenmesi adım adım aşağıda açıklanmıştır.

##  1. Sanal Ortam Oluşturma ve Aktifleştirme

```bash
python -m venv myenv        # Sanal ortam oluşturulur
source myenv/bin/activate   # (Linux/macOS) Ortam aktifleştirilir
# Windows kullanıyorsan:
# myenv\Scripts\activate
```

##  2. Bağımlılıkları Yükleme

```bash
pip install -r requirements.txt  # Gerekli tüm paketler yüklenir
```

##  3. Veritabanı Migrasyonları

```bash
python manage.py makemigrations appuser  # appuser için migration dosyaları oluşturulur
python manage.py makemigrations need     # need için migration dosyaları oluşturulur
python manage.py migrate                 # Veritabanı tabloları oluşturulur
```

## 4. İzleyici (watcher) Scriptini Başlatma

```bash
python watcher.py  # Dosya değişikliklerini izlemek için başlatılır
```

---