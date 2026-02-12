# Clarus Roadmap - Issue Groups

Bu klasör, GitHub issue'larını mantıksal gruplar halinde organize eder. Her grup birbiriyle ilişkili issue'ları içerir ve bir AI agent'a veya geliştiriciye toplu olarak verilebilir.

## Grup Listesi

| Grup | Dosya | Issue Sayısı | Öncelik |
|------|-------|--------------|---------|
| [AI & Agent Sistemi](./01-ai-agent-system.md) | 2 issue | HIGH |
| [Arama & Query](./02-search-query.md) | 4 issue | HIGH |
| [Kelime Arama & Etimoloji](./03-keyword-etymology.md) | 6 issue | MEDIUM |
| [UX & Onboarding](./04-ux-onboarding.md) | 4 issue | MEDIUM |
| [Fizibilite Araştırmaları](./05-feasibility-research.md) | 6 issue | LOW |
| [Monetization](./06-monetization.md) | 1 issue | LOW |

## Önerilen Uygulama Sırası

```
Phase 1 (Sprint 1-2): Temel Geliştirmeler
├── 02-search-query.md (Arama iyileştirmeleri)
└── 03-keyword-etymology.md (Kelime arama genişletme)

Phase 2 (Sprint 3-4): AI & UX
├── 01-ai-agent-system.md (Otonom Agent, Seçici Karşılaştırma)
└── 04-ux-onboarding.md (Dashboard, Onboarding)

Phase 3 (Sprint 5+): Altyapı
├── 05-feasibility-research.md (Altyapı kararları)
└── 06-monetization.md (Polar.sh)
```

## Tamamlanan Issue'lar

| # | Başlık | Tamamlanma |
|---|--------|------------|
| ~~#50~~ | İki Ayrı AI Agent (Kuran + İncil) + Sentez AI | 2026-02-05 |
| ~~#51~~ | Query Modelleri için Hızlı Model Geçişi (flash-lite) | 2026-02-05 |
| ~~#60~~ | Arapça Kelime Etimoloji Popup | 2026-02-11 |
| ~~#67~~ | Etimoloji ↔ Kelime Arama Çift Yönlü Navigasyon — ileri yön var, ters yön gereksiz | 2026-02-12 |

## Birleştirilmesi Önerilen Issue'lar

> **#68 + #70 + #72 → "Akıllı Keyword Search" paketi**
>
> Bu 3 issue birbirine bağımlı ve örtüşüyor. Ayrı ayrı değil, tek grup olarak planlanmalı.
> Detay: [`03-keyword-etymology.md`](./03-keyword-etymology.md#68-70-72--birlikte-planlanmalı)

## Kaldırılan Issue'lar

Aşağıdaki issue'lar scope dışı bırakıldı:
- ~~#53~~ Ruhsal Celseler Modülü
- ~~#54~~ Birleşik Arama (Celseler + Kutsal Kitaplar)
- ~~#59~~ Cohere Reranker Fizibilite

## Kullanım

Her grup dosyası şunları içerir:
1. **Özet**: Grubun amacı
2. **Issue Listesi**: İlgili GitHub issue'ları
3. **Bağımlılık Grafiği**: Hangi issue'ların önce yapılması gerektiği
4. **Tahmini Efor**: Story points veya gün cinsinden
5. **Agent Prompt**: AI agent'a verilebilecek hazır prompt

---

*Son güncelleme: 2026-02-12*
