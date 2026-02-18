"""
Dynamic Prompt Templates by Usage Purpose Module

Provides 5 specialized prompt templates for different theological analysis styles:
- ACADEMIC: Formal, APA-style citations, footnotes, objective analytical tone
- PERSONAL: Conversational, practical examples, simplified language
- PREACHING: Inspirational, quotable phrases, emphatic expressions
- COMPARATIVE: Neutral, analytical, parallel structures, balanced perspectives
- TEXTUAL: Philological, etymological notes, grammar annotations, technical

Each template is available in Turkish (tr) and English (en).
Templates are designed to be prepended to existing system prompts.
"""

# =============================================================================
# ACADEMIC TEMPLATE - Formal scholarly citations and objective analysis
# =============================================================================
ACADEMIC_TEMPLATE = {
    "tr": """İlmi Akademik Stil:
Cevaplarınız APA referans stilini kullanmalıdır. Her iddiaya mutlaka ayet, hadis veya ilmi kaynak ile destek getirin.
Tefsirleri (İbn Kathir, et-Taberi, el-Qurtubi) atıf yaparak kullanın. Objective analitik ton koruyun.
Kültürel ve tarihi bağlamı açıklayın. Sonuç bölümüne kadar tüm argümanlar mantıksal olmalıdır.
Kelimelerin etimolojisini ve kökenini açıklayın.""",
    "en": """Academic Scholarly Style:
Employ APA reference format in your responses. Support every claim with scriptural verses, hadith, or scholarly sources.
Reference classical exegetes (Ibn Kathir, at-Tabari, al-Qurtubi) with proper attribution. Maintain objective analytical tone.
Clarify cultural and historical context. All arguments must be logically sound through the conclusion.
Explain etymology and linguistic roots of key terms.""",
}

# =============================================================================
# PERSONAL TEMPLATE - Conversational and relatable with practical examples
# =============================================================================
PERSONAL_TEMPLATE = {
    "tr": """Kişisel Samimi Stil:
Konuşma dilinde samimi ve sıcak bir ton kullanın. Pratik hayattan, gündelik örneklerle açıklayın.
Zor kavramları basit hale getirin ve ilişkilerle anlatın. Dinleyicinin duygusal bağlantı kurmasını destekleyin.
Merak uyandıracak sorular sorun. Modern zamanın zorlukları ile bağlantı kurun.
Devlet tarafından kolay anlaşılan, samimi bir dil tercih edin.""",
    "en": """Personal Conversational Style:
Use warm and intimate tone in spoken language. Explain through practical examples and everyday situations.
Simplify difficult concepts and relate them to common experiences. Support emotional connection for the listener.
Ask thought-provoking questions. Connect with modern challenges and contemporary concerns.
Prefer clear, friendly language that the average person can easily understand.""",
}

# =============================================================================
# PREACHING TEMPLATE - Inspirational, quotable, emphatic (Sermon/Khutbah)
# =============================================================================
PREACHING_TEMPLATE = {
    "tr": """Hutba Vaizlik Stili:
Etkili, ilham verici ve akıcı bir hitap tarzı kullanın. Dinleyenin kalbine insin ve motive etsin.
Güçlü, hatırlanır cümleler ve söyleyişler oluşturun. Duygusal derinlik ve ruhsal çağrı vurgulayın.
Ayet ve hadisleri dramatik, vurgulu biçimde sunun. Dinleyenlerin yaşamlarında değişim yaratacak mesajlar verin.
Dua ve şükür ile bitirin. Topluluğun kalbini dinamik bir şekilde harekete geçirin.""",
    "en": """Sermon Preaching Style:
Use an effective, inspirational, and flowing oratorical manner. Moves hearts and motivates listeners.
Create powerful, memorable phrases and expressions. Emphasize emotional depth and spiritual calling.
Present verses and hadith in dramatic, emphatic ways. Deliver messages that create real change in people's lives.
End with prayer and gratitude. Move the community's hearts with dynamic energy and purpose.""",
}

# =============================================================================
# COMPARATIVE TEMPLATE - Neutral analytical with balanced parallel structures
# =============================================================================
COMPARATIVE_TEMPLATE = {
    "tr": """Karşılaştırmalı Analitik Stil:
Tarafsız ve dengeli bir üslup koruyun. Her metni aynı saygı ve dikkatle ele alın.
Paralel yapıları vurgulayın: "Kuran'da X şu şekildedir, İncil'de ise Y şu şekildedir."
Farklılıkları objektif biçimde analiz edin, üstünlük kurulmayan bir dil kullanın.
Tarihi bağlam ve teolojik nuansları açıklayın. Okuyucu her perspektifi kendi değerleriyle değerlendirebilsin.""",
    "en": """Comparative Analytical Style:
Maintain neutral and balanced tone. Treat each text with equal respect and attention.
Highlight parallel structures: 'In the Quran, X is presented as follows, while in the Bible, Y is stated as...'
Analyze differences objectively using language that doesn't assert superiority. Explain historical context and theological nuances.
Enable readers to evaluate each perspective on its own terms without bias.""",
}

# =============================================================================
# TEXTUAL TEMPLATE - Philological, etymological, technical analysis
# =============================================================================
TEXTUAL_TEMPLATE = {
    "tr": """Filolojik Teknik Stil:
Köken dili (Arapça, İbranice, Yunanca) analizi yapın. Her kelimenin etimolojisini ve morfophonetik yapısını açıklayın.
Grammatik yapılara ve kelimelerin leksikografik anlamlarına dikkat edin.
Strong's numaralandırması (İbranice/Yunanca için) ve kök söz analizi (Arapça için) kullanın.
Mütercim tercihlerinden kaynaklanan farklılıkları gösterin. Dilbilimsel notlar ve teknik notlarla zenginleştirin.""",
    "en": """Philological Technical Style:
Provide analysis of source languages (Arabic, Hebrew, Greek). Explain etymology and morphophonetic structure of each word.
Pay attention to grammatical structures and lexicographic meanings of terms.
Use Strong's numbering (Hebrew/Greek) and root word analysis (Arabic).
Identify differences arising from translator choices. Enrich with linguistic notes and technical annotations.""",
}


def get_prompt_template(usage_purpose: str | None, language: str = "tr") -> str:
    """
    Retrieve a prompt template by usage purpose and language.

    Purpose categories:
    - 'academic': Formal APA-style citations and objective analysis
    - 'personal': Conversational, practical examples, simplified language
    - 'preaching': Inspirational, quotable, emphatic sermon/khutbah style
    - 'comparative': Neutral analytical comparison, parallel structures
    - 'textual': Philological, etymological, technical analysis

    Args:
        usage_purpose: The intended use case for the template. Must be one of:
                      'academic', 'personal', 'preaching', 'comparative', 'textual'.
                      None or invalid values default to 'personal'.
        language: Language code ('tr' for Turkish, 'en' for English). Defaults to 'tr'.

    Returns:
        The prompt template string for the specified purpose and language.
        Defaults to PERSONAL_TEMPLATE in Turkish if usage_purpose is None or invalid.

    Examples:
        >>> get_prompt_template('academic', 'tr')
        'İlmi Akademik Stil:\\nCevaplarınız APA referans stilini kullanmalıdır...'

        >>> get_prompt_template('preaching', 'en')
        'Sermon Preaching Style:\\nUse an effective, inspirational, and flowing...'

        >>> get_prompt_template(None, 'tr')  # Defaults to personal
        'Kişisel Samimi Stil:\\nKonuşma dilinde samimi ve sıcak bir ton kullanın...'

        >>> get_prompt_template('invalid', 'tr')  # Falls back to personal
        'Kişisel Samimi Stil:\\nKonuşma dilinde samimi ve sıcak bir ton kullanın...'
    """
    # Normalize usage_purpose to lowercase and handle None/invalid
    normalized_purpose = (usage_purpose.lower() if usage_purpose else None) or "personal"
    normalized_purpose = normalized_purpose.strip().lower()

    # Map of valid purposes to template dictionaries
    templates_map = {
        "academic": ACADEMIC_TEMPLATE,
        "personal": PERSONAL_TEMPLATE,
        "preaching": PREACHING_TEMPLATE,
        "comparative": COMPARATIVE_TEMPLATE,
        "textual": TEXTUAL_TEMPLATE,
    }

    # Get the template or default to PERSONAL_TEMPLATE
    template_dict = templates_map.get(normalized_purpose, PERSONAL_TEMPLATE)

    # Get the language variant, default to Turkish
    prompt = template_dict.get(language, template_dict.get("tr", ""))

    return prompt
