# Qdrant Data Persistence Fix

## Context

### Original Request
Qdrant koleksiyonları her Docker restart veya bilgisayar yeniden başlatma sonrası kayboluyor.

### Root Cause Analysis
**Problem**: Docker Desktop 4.55.0 on Ubuntu bind mount (`./qdrant_data:/qdrant/storage`) ile filesystem arasında senkronizasyon sorunu yaşıyor.

**Evidence**:
- Host `qdrant_data/collections/`: 4 koleksiyon MEVCUT (bible_apocrypha, bible_nt, bible_ot, quran_tr)
- Container `/qdrant/storage/collections/`: BOŞ
- Qdrant API: `{"collections": []}`

**Solution**: Named volume (`qdrant_storage`) kullanmak. Docker Desktop ile %100 güvenilir.

---

## Work Objectives

### Core Objective
Docker Desktop ile uyumlu named volume kullanarak Qdrant verilerinin kalıcılığını sağlamak.

### Concrete Deliverables
- `docker-compose.yml` güncellendi (named volume)
- Mevcut koleksiyonlar korunarak yeni volume'a aktarıldı
- Restart sonrası persistence doğrulandı

### Definition of Done
- [x] `docker compose down && docker compose up -d` sonrası koleksiyonlar mevcut
- [x] `curl localhost:6333/collections` 4 koleksiyon döndürüyor

### Must Have
- Mevcut veri korunmalı (43,055+ verse)
- restart: unless-stopped korunmalı

### Must NOT Have (Guardrails)
- Bind mount (`./qdrant_data`) kullanılmamalı
- Veri kaybı olmamalı
- Port değişikliği yapılmamalı

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (automated tests not applicable)
- **User wants tests**: Manual verification
- **QA approach**: Terminal commands + API checks

---

## Task Flow

```
Task 1 (docker-compose.yml) → Task 2 (migrate data) → Task 3 (verify)
```

---

## TODOs

- [x] 1. Update docker-compose.yml to use Named Volume

  **What to do**:
  1. Edit `docker-compose.yml` line 29: change `./qdrant_data:/qdrant/storage` to `qdrant_storage:/qdrant/storage`
  2. Add `qdrant_storage:` to the `volumes:` section at the bottom (line 48)

  **Exact change**:
  ```yaml
  # BEFORE (line 29):
  volumes:
    - ./qdrant_data:/qdrant/storage
  
  # AFTER:
  volumes:
    - qdrant_storage:/qdrant/storage
  
  # AND add to volumes section (line 48):
  volumes:
    postgres_data:
    qdrant_storage:
  ```

  **Must NOT do**:
  - Port değişikliği
  - GRPC_PORT ayarını silme
  - restart policy değişikliği

  **Parallelizable**: NO (required for task 2)

  **References**:
  - `docker-compose.yml:28-31` - Current Qdrant volume configuration
  - `docker-compose.yml:47-48` - Volumes section

  **Acceptance Criteria**:
  - [x] `grep "qdrant_storage:/qdrant/storage" docker-compose.yml` → match found
  - [x] `docker compose config` → no errors

  **Commit**: YES
  - Message: `fix(docker): use named volume for Qdrant persistence`
  - Files: `docker-compose.yml`

---

- [x] 2. Migrate Existing Data to Named Volume

  **What to do**:
  1. Stop current container: `docker compose stop qdrant`
  2. Create new volume: `docker volume create qdrant_storage`
  3. Copy data using temporary container:
     ```bash
     docker run --rm \
       -v /home/freyja/qdrant/qdrant_data:/source:ro \
       -v qdrant_storage:/dest \
       alpine sh -c "cp -av /source/. /dest/"
     ```
  4. Restart with new config: `docker compose up -d qdrant`

  **Must NOT do**:
  - Delete original `qdrant_data/` directory (keep as backup)
  - Use `docker cp` (doesn't work with volumes)

  **Parallelizable**: NO (depends on task 1)

  **References**:
  - `qdrant_data/collections/` - Source data (43,055+ vectors)

  **Acceptance Criteria**:
  - [x] `docker volume inspect qdrant_storage` → volume exists
  - [x] `docker exec holly-qdrant ls /qdrant/storage/collections/` → shows 4 directories
  - [x] Container logs show no errors: `docker logs holly-qdrant --tail 10`

  **Commit**: NO (grouped with verification)

---

- [x] 3. Verify Persistence After Restart

  **What to do**:
  1. Full restart: `docker compose down && docker compose up -d`
  2. Wait for Qdrant ready: `sleep 5`
  3. Verify collections via API

  **Parallelizable**: NO (depends on task 2)

  **References**:
  - Qdrant API: `http://localhost:6333/collections`

  **Acceptance Criteria**:
  - [x] `curl -s localhost:6333/collections | grep -c "quran_tr\|bible_ot\|bible_nt\|bible_apocrypha"` → 4
  - [x] Point counts verified:
    ```bash
    curl -s localhost:6333/collections/quran_tr | grep -o '"points_count":[0-9]*'
    # Expected: "points_count":6236
    ```
  - [x] CLI test: `python main.py info` → shows all collections

  **Commit**: NO

---

- [x] 4. Cleanup and Documentation

  **What to do**:
  1. Update `memory-bank/activeContext.md` with fix details
  2. Optionally archive old bind mount directory (after confirming everything works)

  **Must NOT do**:
  - Delete `qdrant_data/` immediately (keep 1 week as backup)

  **Parallelizable**: YES (independent)

  **Acceptance Criteria**:
  - [x] `memory-bank/activeContext.md` updated with persistence fix notes

  **Commit**: YES
  - Message: `docs: update context with Qdrant persistence fix`
  - Files: `memory-bank/activeContext.md`

---

## Commit Strategy

| After Task | Message | Files |
|------------|---------|-------|
| 1 | `fix(docker): use named volume for Qdrant persistence` | docker-compose.yml |
| 4 | `docs: update context with Qdrant persistence fix` | memory-bank/activeContext.md |

---

## Success Criteria

### Verification Commands
```bash
# Collections exist
curl -s localhost:6333/collections | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['result']['collections']))"
# Expected: 4

# Data persists after restart
docker compose restart qdrant && sleep 5
curl -s localhost:6333/collections/quran_tr | grep points_count
# Expected: "points_count":6236
```

### Final Checklist
- [x] 4 koleksiyon mevcut (quran_tr, bible_ot, bible_nt, bible_apocrypha)
- [x] 43,055+ vektör korundu
- [x] `docker compose down && up` sonrası veriler kalıcı
- [x] Bind mount dizini backup olarak mevcut
