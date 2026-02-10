# Grup 1: AI & Agent Sistemi

## Özet

Mevcut multi-agent sistemini geliştirme ve yeni otonom agent yetenekleri ekleme. Kullanıcıya daha akıllı, daha esnek bir arama ve analiz deneyimi sunma.

## Issue Listesi

| # | Başlık | Öncelik | Efor | Durum |
|---|--------|---------|------|-------|
| ~~[#50](https://github.com/aliozdenisik/Clarus/issues/50)~~ | ~~İki Ayrı AI Agent (Kuran + İncil) + Sentez AI~~ | ~~HIGH~~ | ~~5 gün~~ | ✅ DONE |
| ~~[#51](https://github.com/aliozdenisik/Clarus/issues/51)~~ | ~~Query Modelleri için Hızlı Model Geçişi (flash-lite)~~ | ~~HIGH~~ | ~~1 gün~~ | ✅ DONE |
| [#65](https://github.com/aliozdenisik/Clarus/issues/65) | Seçici Kitap Karşılaştırma (Min 2 Kaynak) | MEDIUM | 2 gün | 🔲 TODO |
| [#71](https://github.com/aliozdenisik/Clarus/issues/71) | Otonom AI Agent (Keyword + Semantic Birleşik) | HIGH | 8 gün | 🔲 TODO |

## Kalan İşler

| # | Başlık | Öncelik | Efor |
|---|--------|---------|------|
| [#65](https://github.com/aliozdenisik/Clarus/issues/65) | Seçici Kitap Karşılaştırma (Min 2 Kaynak) | MEDIUM | 2 gün |
| [#71](https://github.com/aliozdenisik/Clarus/issues/71) | Otonom AI Agent (Keyword + Semantic Birleşik) | HIGH | 8 gün |

## Bağımlılık Grafiği

```
#65 (Seçici Karşılaştırma) ───────► #71 (Otonom Agent)
```

**Önerilen Sıra:**
1. `#65` - Seçici karşılaştırma (mevcut compare'e ekleme)
2. `#71` - Otonom Agent (en karmaşık, #65'e bağlı)

## Tahmini Toplam Efor

**10 gün** (1 geliştirici)

## Teknik Notlar

### Paylaşılan Bileşenler
- `backend/src/multi_agent_answer_generator.py` - Agent logic
- `backend/app/api/compare.py` - API endpoint değişiklikleri
- `frontend/app/compare/page.tsx` - UI değişiklikleri

## Agent Prompt

```
Bu gruptaki 2 issue'yu sırayla uygula:

1. ÖNCE #65'i yap: Compare page'de collection checkbox'ları ekle.
   - Minimum 2 seçim zorunlu, 1 seçilirse /search'e redirect
   - Backend: collections parametresi ekle, validate et
   - Frontend: CollectionSelector component
   - Seçilmeyen ajanlar çalışmaz

2. SONRA #71'i yap: Otonom agent.
   - Query analyzer ile intent detection
   - keyword/semantic/hybrid karar verme
   - Tool execution (keyword search, semantic search)
   - Result fusion
   - Yeni /smart-search sayfası

Her issue için:
- Kodu yaz
- Test ekle
- lsp_diagnostics ile kontrol et
- Commit at (issue referansı ile)
```

## Kabul Kriterleri Özeti

- [ ] #65: Collection seçimi çalışıyor, min 2 validation
- [ ] #71: Smart search intent detection çalışıyor
