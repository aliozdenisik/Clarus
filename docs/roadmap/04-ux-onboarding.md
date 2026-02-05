# Grup 4: UX & Onboarding

## Özet

Kullanıcı deneyimini iyileştiren özellikler: dashboard ana sayfa, onboarding süreci, sesli okuma, ve TTS entegrasyonu.

## Issue Listesi

| # | Başlık | Öncelik | Efor |
|---|--------|---------|------|
| [#74](https://github.com/aliozdenisik/Clarus/issues/74) | Dashboard/Hub Ana Sayfa | MEDIUM | 2 gün |
| [#64](https://github.com/aliozdenisik/Clarus/issues/64) | Onboarding Süreci (Akademik Format vb.) | MEDIUM | 3 gün |
| [#69](https://github.com/aliozdenisik/Clarus/issues/69) | ElevenLabs Sesli Okuma (TTS) | LOW | 3 gün |
| [#70](https://github.com/aliozdenisik/Clarus/issues/70) | Arapça Bilgi Seviyesi Kontrolü | LOW | 2 gün |

> Not: #70 hem bu grupta hem Grup 3'te (Kelime Arama) yer alıyor. Onboarding ile birlikte yapılması önerilir.

## Bağımlılık Grafiği

```
#64 (Onboarding) ◄─────────────────────────────┐
         │                                     │
         ▼                                     │
#70 (Arapça Seviye) ───────────────────────────┤
         │                                     │
         ▼                                     │
#74 (Dashboard) ◄──────────────────────────────┘
                                               │
#69 (TTS) ─────────────────────────────────────┘
                                               │
                                               ▼
                                    [User Experience]
```

**Önerilen Sıra:**
1. `#74` - Dashboard (login sonrası landing)
2. `#64` - Onboarding (yeni kullanıcı akışı)
3. `#70` - Arapça seviye (onboarding parçası)
4. `#69` - TTS (bağımsız, paralel yapılabilir)

## Tahmini Toplam Efor

**10 gün** (1 geliştirici)

## Teknik Notlar

### Dashboard Layout
```
┌─────────────────────────────────────────────────────────────┐
│  Hoş geldiniz, [Kullanıcı]                                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Arama   │  │Karşılaş.│  │ Kelime  │  │ Browse  │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│  ┌─────────┐  ┌─────────┐                                   │
│  │ Geçmiş  │  │ Ayarlar │                                   │
│  └─────────┘  └─────────┘                                   │
├─────────────────────────────────────────────────────────────┤
│  📊 Son Aktivite                                            │
│  • "Sabır kavramı" - 2 saat önce                           │
│  • "Creation story" - dün                                   │
└─────────────────────────────────────────────────────────────┘
```

### Onboarding Wizard
```typescript
const ONBOARDING_STEPS = [
  'welcome',      // Hoş geldiniz
  'purpose',      // Kullanım amacı (akademik, kişisel, vaaz)
  'language',     // Tercih edilen dil
  'arabic',       // Arapça seviyesi
  'interests',    // İlgi alanları
  'complete'      // Tamamlandı
];
```

### TTS Integration
```python
# ElevenLabs API
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_AR = "arabic-reciter-id"
ELEVENLABS_VOICE_TR = "turkish-narrator-id"
```

## Agent Prompt

```
Bu gruptaki 4 issue'yu sırayla uygula:

1. ÖNCE #74'ü yap: Dashboard sayfası.
   - /dashboard route oluştur
   - 6 feature card (Search, Compare, Keyword, Browse, History, Settings)
   - Son aktivite listesi (API: GET /api/users/activity)
   - Login redirect: /search → /dashboard
   - Responsive grid (mobile: 1 col, desktop: 3 col)

2. SONRA #64'ü yap: Onboarding wizard.
   - /onboarding route
   - 5 step wizard component
   - UserPreferences model'e yeni alanlar:
     * usage_purpose: akademik | personal | preaching | comparative | textual
     * onboarding_completed: boolean
   - Tamamlanmadıysa dashboard'dan redirect
   - Skip seçeneği

3. SONRA #70'i yap: Arapça seviye.
   - UserPreferences.arabic_proficiency: none | basic | intermediate | advanced
   - Onboarding step olarak entegre et (veya ayrı settings)
   - Keyword search UI adaptasyonu

4. EN SON #69'u yap: ElevenLabs TTS.
   - POST /api/tts endpoint
   - ElevenLabs API integration
   - Redis cache (generated audio)
   - VersePlayer component (play/pause)
   - Rate limiting (free tier: 10K chars/month)

Her issue için test yaz ve commit at.
```

## Kabul Kriterleri Özeti

- [ ] #74: Login sonrası /dashboard açılıyor
- [ ] #74: 6 feature card tıklanabilir
- [ ] #64: Yeni kullanıcı onboarding'e yönleniyor
- [ ] #64: 5 step tamamlanabiliyor
- [ ] #70: Arapça seviye seçimi keyword search'i etkiliyor
- [ ] #69: Ayet play butonu Arapça okuyor

## Cost Considerations

### ElevenLabs Pricing (#69)
| Plan | Limit | Cost |
|------|-------|------|
| Free | 10K chars/mo | $0 |
| Starter | 30K chars/mo | $5/mo |
| Creator | 100K chars/mo | $22/mo |

Average verse: ~150 chars → ~65 unique verses/month at free tier
