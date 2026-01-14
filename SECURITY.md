# 🔐 Security Policy

Security policy and best practices for the Sacred Texts Ultimate RAG Search project.

---

## 📋 Table of Contents

- [API Key Security](#-api-key-security)
- [Environment Variables](#-environment-variables)
- [Qdrant Database Security](#-qdrant-database-security)
- [Data Security](#-data-security)
- [Reporting a Vulnerability](#-reporting-a-vulnerability)
- [Supported Versions](#-supported-versions)

---

## 🔑 API Key Security

### Required API Keys

| Service | Variable Name | Purpose |
|---------|---------------|---------|
| OpenRouter | `OPENROUTER_API_KEY` | LLM queries (Gemini) |
| SiliconFlow | `SILICONFLOW_API_KEY` | Reranker (Qwen3) |

### ⚠️ Important Rules

1. **Never commit API keys**
   ```bash
   # Ensure this line exists in .gitignore
   .env
   ```

2. **Never hardcode keys in source code**
   ```python
   # ❌ WRONG
   api_key = "sk-abc123..."
   
   # ✅ CORRECT
   api_key = os.getenv("OPENROUTER_API_KEY")
   ```

3. **Rotate keys regularly**
   - Renew keys every 90 days
   - Change immediately if suspicious activity is detected

---

## 🌍 Environment Variables

### `.env` File Template

```env
# === API Keys ===
OPENROUTER_API_KEY=your-openrouter-key
SILICONFLOW_API_KEY=your-siliconflow-key

# === Optional Settings ===
QDRANT_HOST=localhost
QDRANT_PORT=6333
# QDRANT_API_KEY=your-qdrant-api-key  # Enable if using authentication
```

### File Permissions

```bash
# Restrict .env file to owner only
chmod 600 .env
```

---

## 🗄️ Qdrant Database Security

### Local Development

Default Docker setup runs without authentication:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Production Environment Recommendations

1. **Enable API Key Authentication**
   ```yaml
   # config.yaml
   service:
     api_key: "generate-a-strong-random-key"
   ```

2. **Use TLS/HTTPS**
   ```bash
   docker run -p 6333:6333 \
     -v $(pwd)/tls:/qdrant/tls:ro \
     -e QDRANT__SERVICE__ENABLE_TLS=true \
     qdrant/qdrant
   ```

3. **Network Isolation**
   - Do not expose Qdrant port externally
   - Use Docker networks or VPN

4. **Regular Backups**
   ```bash
   # Create snapshot
   curl -X POST 'http://localhost:6333/collections/quran_tr/snapshots'
   ```

---

## 📊 Data Security

### Stored Data

| Collection | Content | Sensitivity |
|------------|---------|-------------|
| `quran_tr` | Quran verses (Turkish) | Low |
| `quran_tr_semantic_chunks` | Semantic groups | Low |
| `bible_kjva` | Bible (KJVA) | Low |
| `bible_kjva_semantic_chunks` | Semantic groups | Low |

### Cache Security

- Cache files are stored in `cache/` directory
- May contain sensitive query data
- Be cautious on shared systems

```bash
# Clear cache
python main.py cache-clear
```

---

## 🚨 Reporting a Vulnerability

### Reporting Process

1. **Keep it confidential**: Do not disclose publicly
2. **Provide detailed report**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

3. **Contact**:
   - Open a **private** issue on GitHub
   - Or contact the project maintainer directly

### Response Timeline

| Phase | Timeframe |
|-------|-----------|
| Initial response | Within 48 hours |
| Assessment | Within 7 days |
| Patch release | Critical: 7 days, Medium: 30 days |

### Out of Scope

- DoS attacks (designed for local/private use)
- Social engineering
- Physical access attacks

---

## 📦 Supported Versions

| Version | Status | Notes |
|---------|--------|-------|
| `main` branch | ✅ Active | Latest, supported |
| Older commits | ❌ Unsupported | Please upgrade |

---

## 🛡️ Security Checklist

Verify before deploying to production:

- [ ] `.env` file is in `.gitignore`
- [ ] API keys are strong and unique
- [ ] Qdrant API key enabled (for production)
- [ ] TLS/HTTPS enabled (for production)
- [ ] File permissions restricted (`chmod 600 .env`)
- [ ] Regular backup plan in place
- [ ] Cache data reviewed

---

## 📚 Additional Resources

- [Qdrant Security Best Practices](https://qdrant.tech/documentation/guides/security/)
- [OpenRouter API Docs](https://openrouter.ai/docs)
- [OWASP API Security](https://owasp.org/www-project-api-security/)

---

*Last updated: January 2026*
