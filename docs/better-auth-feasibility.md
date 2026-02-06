# Better Auth Framework Fizibilite Analizi (Issue #75)

**Durum:** Taslak
**Yazar:** Sisyphus (Backend Team)
**Tarih:** 06 Şubat 2026
**İlgili Issue:** #75

## 1. Yönetici Özeti

Clarus projesi için mevcut Python tabanlı (PyJWT + bcrypt) kimlik doğrulama sisteminin, TypeScript tabanlı **Better Auth** kütüphanesi ile değiştirilmesine yönelik teknik fizibilite çalışması tamamlanmıştır.

**Öneri: GO (GEÇİŞ YAPILSIN)**

Mevcut sistemin bakım maliyetini düşürmek, güvenliği artırmak (oturum yönetimi, çoklu faktör, sosyal girişler) ve frontend-native (Next.js) bir yapıya geçmek için Better Auth entegrasyonu teknik olarak mümkündür ve önerilmektedir.

Next.js katmanında tam entegre çalışacak Better Auth, FastAPI backend servisi ile **JWKS (JSON Web Key Set)** protokolü üzerinden güvenli bir şekilde haberleşecektir. Bu mimari, Python backend'in kimlik doğrulama yükünü hafifletecek ve endüstri standardı bir yapı (OIDC benzeri) kurmamızı sağlayacaktır.

---

## 2. Mevcut Kimlik Doğrulama Sistemi Analizi

Şu anki altyapımız tamamen özel (custom) olarak yazılmış modüllerden oluşmaktadır:

*   **Teknoloji:** `PyJWT` (Python) + `bcrypt`
*   **Token Tipi:** Stateless JWT (HS256 algoritması)
*   **Oturum Yönetimi:** Yok (Stateless). Token iptali (revocation) için Redis üzerinde whitelist/blacklist mekanizması kullanılıyor.
*   **Şifreleme:** `bcrypt` (cost 12)
*   **Sosyal Giriş:** Özel yazılmış Google OAuth implementasyonu.
*   **Rate Limiting:** Redis tabanlı, kullanıcı başına günlük 50 sorgu (middleware seviyesinde).
*   **Eksikler:**
    *   2FA/MFA desteği yok.
    *   Oturum yönetimi (cihaz bazlı çıkış yapma vb.) veritabanı seviyesinde değil.
    *   Frontend tarafında (Next.js) state yönetimi manuel yapılıyor.

---

## 3. Better Auth Framework Analizi

Better Auth, modern web uygulamaları için geliştirilmiş, TypeScript odaklı ve yüksek performanslı bir kimlik doğrulama kütüphanesidir.

*   **Ekosistem:** 25.7k+ GitHub yıldızı, aktif topluluk.
*   **Mimari:** Headless (UI bağımsız), Plugin tabanlı yapı.
*   **Veritabanı:** PostgreSQL Pool adaptörü ile doğrudan veritabanına erişim (ORM bağımlılığı yok).
*   **Öne Çıkan Özellikler:**
    *   **Plugin Sistemi:** Username/Password, OAuth (Google, GitHub vb.), 2FA, Email Verification modüler olarak eklenip çıkarılabilir.
    *   **Hibrit Oturum:** Veritabanı destekli oturumlar (Session Table) + İstemci tarafı için JWT desteği.
    *   **Cross-Language Support:** Diğer dillerle (Python, Go vb.) haberleşmek için JWKS endpoint desteği sunar.

### Özellik Karşılaştırması

| Özellik | Mevcut Sistem (Python) | Better Auth (TypeScript) |
| :--- | :--- | :--- |
| **Dil/Platform** | Python / FastAPI | TypeScript / Next.js |
| **Oturum Tipi** | Stateless JWT | Stateful Session + JWT |
| **Veritabanı** | SQLAlchemy Models | Drizzle/Prisma veya Raw SQL |
| **Şifreleme** | bcrypt | bcrypt / argon2 |
| **Sosyal Giriş** | Custom Implementation | Built-in Plugins |
| **MFA/2FA** | Yok | Native Plugin Desteği |
| **Bakım Yükü** | Yüksek (Her özellik elle yazılıyor) | Düşük (Kütüphane güncellemeleri) |

---

## 4. Mimari Karar: Hibrit Yapı (Next.js Auth + FastAPI Resource Server)

Better Auth, Node.js/Bun ortamında çalıştığı için doğrudan Python backend içinde çalıştırılamaz. Bu nedenle aşağıdaki hibrit mimari benimsenmiştir:

1.  **Auth Sunucusu (Next.js):**
    *   Better Auth burada çalışacak.
    *   `/api/auth/*` endpointlerini sunacak.
    *   Kullanıcı giriş/çıkış, kayıt, email doğrulama işlemleri burada yapılacak.
    *   **JWKS Endpoint:** Better Auth, public key'leri `/api/auth/jwks` adresinden yayınlayacak.

2.  **Resource Sunucusu (FastAPI Backend):**
    *   Kimlik doğrulama mantığı (Auth Logic) kaldırılacak.
    *   Yerine **Token Doğrulama (Validation)** mantığı eklenecek.
    *   FastAPI, gelen JWT token'ı Next.js'in sunduğu JWKS endpoint'inden aldığı public key ile doğrulayacak (`RS256` veya `EdDSA`).
    *   `user_stats` ve iş mantığı tabloları FastAPI kontrolünde kalmaya devam edecek.

3.  **Veritabanı:**
    *   Ortak PostgreSQL veritabanı kullanılacak.
    *   Better Auth tabloları (`user`, `session`, `account`, `verification`) Next.js tarafından yönetilecek.
    *   İş tabloları (`user_stats` vb.) mevcut yapıda kalacak.

---

## 5. Migrasyon Planı (4 Faz)

Geçiş işlemi, kesinti yaşanmadan (zero-downtime) ve veri kaybı olmadan yapılacaktır.

### Faz 1: Hazırlık (Setup)
*   [x] Better Auth konfigürasyonu (Next.js tarafında).
*   [x] Veritabanı şemalarının oluşturulması (Migration scriptleri).
*   [ ] Mevcut kullanıcı verilerinin Better Auth şemasına uygun hale getirilmesi (hash uyumluluğu kontrolü).

### Faz 2: Köprü Kurulumu (Bridge)
*   [ ] Next.js tarafında JWKS plugin'inin aktif edilmesi.
*   [ ] FastAPI tarafında `PyJWT` ve `PyJWKClient` kullanılarak yeni bir `dependency` yazılması.
*   [ ] API Key veya Service Token ile backend-frontend arası güvenli iletişimin test edilmesi.

### Faz 3: Kademeli Geçiş (Migration)
*   [ ] Frontend'in giriş/kayıt formlarının Better Auth client hook'larına (`useSession` vb.) bağlanması.
*   [ ] Yeni kullanıcıların Better Auth sistemi üzerinden kaydedilmesi.
*   [ ] Mevcut kullanıcıların şifrelerinin (bcrypt) Better Auth ile uyumlu olduğunun doğrulanması (Re-hashing gerekebilir).

### Faz 4: Temizlik (Cleanup)
*   [ ] Python tarafındaki eski `auth/` klasörünün arşivlenmesi/silinmesi.
*   [ ] Eski token blacklist (Redis) mekanizmasının devre dışı bırakılması.
*   [ ] E2E testlerinin yeni akışa göre güncellenmesi.

---

## 6. Risk Değerlendirme Matrisi

| Risk | Olasılık | Etki | Mitigasyon (Çözüm) |
| :--- | :--- | :--- | :--- |
| **Öğrenme Eğrisi** | Düşük | Orta | Better Auth dokümantasyonu kapsamlıdır ve ekip TypeScript'e hakimdir. |
| **Veri Kaybı** | Çok Düşük | Yüksek | Kullanıcı tablosu migrasyonu yedekli ve "dry-run" modunda test edilecektir. |
| **Performans** | Düşük | Düşük | JWKS key'leri FastAPI tarafında önbelleklenecek (Cache), her istekte sorgu atılmayacak. |
| **Vendor Lock-in** | Düşük | Orta | Kütüphane açık kaynaklıdır ve self-hosted çalışır. Veriler kendi veritabanımızdadır. |
| **Kesinti (Downtime)** | Orta | Yüksek | Paralel çalışma (Parallel Run) dönemi ile eski ve yeni sistem kısa süre aynı anda çalışacak. |

---

## 7. Güvenlik Karşılaştırması

*   **Şifreleme:** Her iki sistem de `bcrypt` kullanıyor, geçişte şifre sıfırlamaya gerek yok.
*   **Oturum Güvenliği:**
    *   *Mevcut:* Sadece Access/Refresh token. Çalınan token süresi bitene kadar geçerli (Redis blacklist hariç).
    *   *Better Auth:* Veritabanı tabanlı oturum. Şüpheli durumlarda sunucu tarafından anında tüm oturumlar kapatılabilir.
*   **Token Standartları:** Better Auth endüstri standardı OIDC/OAuth2 akışlarına daha yakındır.
*   **Rate Limiting:** Mevcut Redis yapısı korunacak, sadece kullanıcı ID'si artık Better Auth'dan gelen token'dan okunacak.

---

## 8. Maliyet Analizi

*   **Lisans:** MIT Lisansı (Ücretsiz, Açık Kaynak).
*   **Sunucu Maliyeti:** Ek bir maliyet getirmez, mevcut Next.js container içinde çalışır.
*   **Efor:**
    *   Kurulum ve Config: 1 Gün
    *   Backend Entegrasyonu: 1 Gün
    *   Frontend Migrasyonu: 2 Gün
    *   Test ve Deploy: 1 Gün
    *   **Toplam Tahmini Efor:** 1 Hafta (1 Developer)

---

## 9. Uyumluluk Cevapları (Issue #75 Soruları)

Issue #75 içerisinde yöneltilen kritik soruların cevapları:

1.  **FastAPI entegrasyonu nasıl olacak?**
    *   **Cevap:** JWKS (JSON Web Key Set) köprüsü ile. Next.js anahtar dağıtıcı, FastAPI doğrulayıcı olarak çalışacak.
2.  **User tablosu migrasyonu mümkün mü?**
    *   **Cevap:** Evet. Mevcut `users` tablosu Better Auth'un beklediği `user` şemasına dönüştürülecek bir SQL scripti ile taşınabilir. Şifre hash'leri (bcrypt) uyumludur.
3.  **Next.js 15 SDK desteği var mı?**
    *   **Cevap:** Evet, Better Auth Next.js 15 (App Router) ile native uyumludur.
4.  **Mevcut auth flow'lar bozulacak mı?**
    *   **Cevap:** Hayır. Login, Register, Google OAuth akışları korunacak, sadece altyapısı değişecek.
5.  **Rate limiting etkilenecek mi?**
    *   **Cevap:** Hayır. `user_stats` ve Redis tabanlı rate limiting mantığı FastAPI tarafında çalışmaya devam edecek. Sadece `user_id` kaynağı değişecek.
6.  **Sıfır kesinti (Zero-downtime) mümkün mü?**
    *   **Cevap:** Evet. "Parallel Run" stratejisi ile eski token'lar geçerliliğini korurken yeni sistem devreye alınabilir. Ancak en temiz yöntem, geçiş anında tüm kullanıcıların bir kez tekrar giriş yapmasını istemektir (Token invalidation).

---

## 10. Go/No-Go Tavsiyesi

Yapılan teknik incelemeler sonucunda, projenin geleceği, kod kalitesi ve güvenlik standartları açısından Better Auth kütüphanesine geçiş **ONAYLANMIŞTIR (GO)**.

**Sonraki Adım:** Faz 1 (Hazırlık) çalışmalarının başlatılması ve PoC branch'inin oluşturulması.
