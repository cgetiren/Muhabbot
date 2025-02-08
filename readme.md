# Voice Chat Uygulaması

## Açıklama
Bu uygulama, Python tabanlı bir masaüstü sesli sohbet uygulamasıdır. PyQt6 kullanılarak geliştirilmiş kullanıcı arayüzü ve SocketIO ile gerçek zamanlı iletişim sağlanmaktadır.

## Özellikler
- Sesli sohbet odaları
- Metin tabanlı sohbet
- Mikrofon ve hoparlör kontrolü
- Ses ayarları (giriş/çıkış cihazı seçimi, ses seviyesi)
- Kullanıcı listesi
- Oda sistemi

## Gereksinimler
- Python 3.8+
- PyQt6 6.5.0
- PyAudio 0.2.13
- Python-SocketIO 5.8.0
- SQLAlchemy 2.0.0
- Diğer gereksinimler `requirements.txt` dosyasında listelenmiştir

## Kurulum
1. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Veritabanını oluşturun:
   Python otomatik olarak SQLite veritabanını oluşturacaktır.

3. Server'ı başlatın:
   ```bash
   python server/server.py
   ```

4. Client'ı başlatın:
   ```bash
   python client/main.py
   ```

## Kullanım
1. Client uygulamasını başlatın
2. Kullanıcı adınızı girin
3. İstediğiniz sohbet odasına katılın
4. Mikrofon ve hoparlör kontrollerini kullanarak sesli sohbete katılın

## Proje Yapısı
client/
├── assets/ # İkonlar ve görsel dosyalar
├── audio/ # Ses yönetimi modülleri
├── network/ # Ağ iletişimi modülleri
├── ui/ # Kullanıcı arayüzü modülleri
└── main.py # Client ana uygulama
server/
├── database.py # Veritabanı yönetimi
├── room_manager.py # Oda yönetimi
└── server.py # Server uygulaması

## Özellikler Detayı
- **Gerçek zamanlı ses iletimi**: Düşük gecikmeli ses aktarımı
- **Metin mesajlaşma**: Anlık mesajlaşma özelliği
- **Oda bazlı kullanıcı yönetimi**: Farklı odalarda farklı kullanıcı grupları
- **Mikrofon testi özelliği**: Ses girişini test etme imkanı
- **Ses seviyesi kontrolü**: Mikrofon ve hoparlör ses seviyesi ayarı
- **Giriş/çıkış cihazı seçimi**: Birden fazla ses cihazı desteği
- **Kullanıcı durumu gösterimi**: Aktif kullanıcıların listesi
- **Animasyonlu ayarlar paneli**: Kullanıcı dostu arayüz

## Teknik Detaylar
- **Frontend**: PyQt6
- **Backend**: Python SocketIO
- **Veritabanı**: SQLite
- **Ses İşleme**: PyAudio
- **Protokol**: WebSocket

## Geliştirici Notları
- Server'ı başlatmadan önce port kullanılabilirliğini kontrol edin
- Ses ayarlarını yaparken sistem ses ayarlarıyla uyumlu olduğundan emin olun
- Mikrofon izinlerinin verildiğinden emin olun

## Hata Ayıklama
- Bağlantı sorunları için port ve firewall ayarlarını kontrol edin
- Ses sorunları için sistem ses ayarlarını kontrol edin
- Log dosyalarını kontrol edin

## Katkıda Bulunma
1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## Lisans
Bu proje MIT lisansı altında lisanslanmıştır.
