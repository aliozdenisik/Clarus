# Grup 6: Monetization

## Özet

Polar.sh entegrasyonu ile sürdürülebilir gelir modeli. Sponsorluk, issue funding, ve opsiyonel premium özellikler.

## Issue Listesi

| # | Başlık | Öncelik | Efor |
|---|--------|---------|------|
| [#76](https://github.com/aliozdenisik/Clarus/issues/76) | Polar.sh Online Ödeme ve Sponsorluk Sistemi | LOW | 2 gün |

## Bağımlılık

```
Önkoşullar:
├── Production deployment ✓
├── User base (beta users)
└── Feature stability

#76 (Polar.sh) ──────► Sustainable funding
                       ├── Sponsor recognition
                       ├── Issue bounties
                       └── (Optional) Premium tier
```

## Monetization Modeli Seçenekleri

### Option A: Sponsorship Only (Önerilen Başlangıç)

```
Tüm özellikler ücretsiz
Gelir kaynağı: Gönüllü sponsorluklar

Pros:
✓ Kullanıcı dostu
✓ Open source ruhu korunur
✓ Hızlı kurulum

Cons:
✗ Gelir belirsiz
✗ Sürdürülebilirlik riski
```

### Option B: Freemium

```
Free:
- 50 searches/day
- Basic compare
- No export

Pro ($9/mo):
- Unlimited searches
- PDF/Word export
- Priority API
- Custom AI formatting

Pros:
✓ Predictable revenue
✓ Clear value proposition

Cons:
✗ Feature gating karmaşık
✗ User friction
```

### Option C: Issue Funding

```
Topluluk belirli issue'ları fonlar
Contributor bounty alır

Pros:
✓ Community-driven development
✓ Transparent priorities

Cons:
✗ Unpredictable
✗ Management overhead
```

## Tahmini Efor

**2 gün** (setup + integration)

## Teknik Entegrasyon

### 1. Polar.sh Dashboard Setup
```
1. polar.sh'a sign up
2. GitHub App install
3. Organization: aliozdenisik
4. Repository: Clarus
5. Sponsorship tiers tanımla
```

### 2. README Badge
```markdown
[![Sponsor](https://img.shields.io/badge/sponsor-Polar.sh-blue)](https://polar.sh/aliozdenisik)
```

### 3. Webhook (Opsiyonel - Premium için)
```python
# backend/app/api/webhooks/polar.py
@router.post("/webhooks/polar")
async def polar_webhook(request: Request):
    payload = await request.json()
    signature = request.headers.get("X-Polar-Signature")
    
    if not verify_signature(payload, signature):
        raise HTTPException(401)
    
    match payload["type"]:
        case "subscription.created":
            user = await get_user_by_email(payload["email"])
            user.tier = "pro"
            await db.commit()
```

### 4. License Check (Premium için)
```python
# backend/app/middleware/license.py
async def check_tier_limit(user: User, action: str):
    if action == "search" and user.tier == "free":
        daily_count = await get_daily_search_count(user.id)
        if daily_count >= 50:
            raise HTTPException(429, "Daily limit reached. Upgrade to Pro.")
```

## Agent Prompt

```
#76'yı uygula: Polar.sh entegrasyonu.

Bu RESEARCH + SETUP issue'su. Minimal kod.

1. Polar.sh Setup:
   - https://polar.sh/ hesap oluştur
   - GitHub App kur (aliozdenisik/Clarus)
   - Sponsorship tiers tanımla:
     * Bronze $5/mo
     * Silver $25/mo
     * Gold $100/mo

2. README güncelle:
   - Polar.sh badge ekle
   - Sponsors section ekle
   - "Support this project" bölümü

3. CONTRIBUTING.md güncelle:
   - Issue bounties açıklaması
   - Sponsor benefits

4. (Opsiyonel) Webhook:
   - Eğer premium tier planlanıyorsa
   - POST /api/webhooks/polar endpoint
   - Subscription event handling

5. Dokümantasyon:
   - docs/monetization/POLAR_SETUP.md
   - Tier açıklamaları
   - Webhook configuration

Commit at: "feat: add Polar.sh sponsorship integration"
```

## Sponsorship Tiers

| Tier | Fiyat | Benefits |
|------|-------|----------|
| 🥉 Bronze | $5/mo | README'de isim, Discord role |
| 🥈 Silver | $25/mo | + Priority support, early access |
| 🥇 Gold | $100/mo | + Logo in README, feature requests |
| 💎 Diamond | $500/mo | + Custom integration, dedicated support |

## Success Metrics

| Metric | Target (6 mo) | Target (1 yr) |
|--------|---------------|---------------|
| Total Sponsors | 10 | 50 |
| MRR | $100 | $500 |
| Issue Bounties Paid | 3 | 10 |

## Kabul Kriterleri

- [ ] Polar.sh organization aktif
- [ ] README'de sponsor badge var
- [ ] En az 1 sponsorship tier aktif
- [ ] (Opsiyonel) Webhook çalışıyor
- [ ] Dokümantasyon tamamlandı
