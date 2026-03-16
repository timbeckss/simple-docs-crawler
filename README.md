# Universal Documentation Crawler

Ein leistungsstarker Python-basierter Web-Crawler, der Dokumentations-Websites crawlt und als saubere, LLM-optimierte Markdown-Dateien speichert.

## Features

✅ **Zwei Crawl-Modi:**
- **Normal-Modus**: Folgt Links auf der Website bis zu einer konfigurierbaren Tiefe (BFS-Strategie)
- **Sitemap-Modus**: Parst `sitemap.xml` und crawlt alle aufgelisteten URLs direkt

✅ **Intelligente Filterung:**
- Domain-Filter (nur gleiche Domain)
- URL-Präfix-Filter (z.B. nur `/api/` oder `/docs/`)
- Konfigurierbare HTML-Element-Ausschlüsse (Navigation, Footer, etc.)

✅ **LLM-Optimierung:**
- Saubere Markdown-Konvertierung
- Automatische `llms.txt` Index-Generierung
- Strukturierte Datei-Organisation

✅ **Sitemap-Support:**
- Standard `sitemap.xml` Format
- Sitemap-Index-Dateien (mit mehreren Sub-Sitemaps)
- Automatische URL-Deduplizierung

## Installation

### 1. Repository klonen oder Datei herunterladen

```bash
git clone <your-repo-url>
cd crawl4ai-project
```

### 2. Virtuelle Umgebung erstellen (empfohlen)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

**Benötigte Pakete:**
- `crawl4ai` - Web-Crawling-Framework
- `aiohttp` - Async HTTP-Client für Sitemap-Fetching

## Verwendung

### Normal-Modus (Link-Following)

```bash
# Einfaches Crawling mit Standard-Konfiguration
python crawl_docs.py

# Spezifische URL crawlen
python crawl_docs.py --url https://docs.example.com

# Mit URL-Präfix-Filter (nur /api/* Seiten)
python crawl_docs.py --url https://docs.example.com --prefix /api

# Crawl-Tiefe anpassen
python crawl_docs.py --url https://docs.example.com --depth 3

# Custom Output-Verzeichnis
python crawl_docs.py --url https://docs.example.com --out ./my-docs

# llms.txt Index generieren
python crawl_docs.py --url https://docs.example.com --llms-txt
```

### Sitemap-Modus

```bash
# Sitemap parsen und alle URLs crawlen
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap

# Sitemap mit Präfix-Filter (nur URLs die mit /docs beginnen)
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap --prefix /docs

# Sitemap mit llms.txt Index
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap --llms-txt
```

**Hinweis:** Im Sitemap-Modus wird die `--depth` Option ignoriert, da alle URLs direkt aus der Sitemap extrahiert werden.

### Alle Optionen

```
--url URL              Start-URL zum Crawlen
--prefix PREFIX        Nur URLs mit diesem Pfad-Präfix crawlen
--depth DEPTH          Maximale Crawl-Tiefe (Standard: 5)
--out OUTPUT_DIR       Output-Verzeichnis (Standard: ./remnote-docs)
--exclude SELECTORS    CSS-Selektoren zum Entfernen (z.B. "nav, footer")
--llms-txt             llms.txt Index-Datei generieren
--from-sitemap         Sitemap-Modus aktivieren
```

## Konfiguration

Die Standard-Konfiguration kann in [`crawl_docs.py`](crawl_docs.py:24) angepasst werden:

```python
CONFIG = {
    "url": "https://plugins.remnote.com/sitemap.xml",
    "url_prefix": "",
    "max_depth": 5,
    "output_dir": "./remnote-docs",
    "excluded_selectors": "nav, footer, .sidebar, .navbar, header, .toc, [role='navigation']",
    "generate_llms_txt": True,
    "from_sitemap": False,
}
```

## Beispiele

### Beispiel 1: RemNote Plugin Dokumentation

```bash
python crawl_docs.py --url https://plugins.remnote.com/sitemap.xml --from-sitemap --llms-txt
```

### Beispiel 2: Nur API-Dokumentation crawlen

```bash
python crawl_docs.py --url https://docs.example.com --prefix /api/v2 --depth 3
```

### Beispiel 3: Mehrere Sitemaps (Sitemap-Index)

```bash
python crawl_docs.py --url https://example.com/sitemap_index.xml --from-sitemap
```

## Output-Struktur

Gecrawlte Seiten werden als Markdown-Dateien gespeichert, die die URL-Struktur widerspiegeln:

```
output_dir/
├── index.md                          # Startseite
├── api/
│   ├── classes/
│   │   ├── Rem/index.md
│   │   └── Query/index.md
│   └── enums/
│       └── RemType/index.md
└── llms.txt                          # Automatisch generierter Index (optional)
```

## llms.txt Format

Wenn `--llms-txt` aktiviert ist, wird eine strukturierte Index-Datei generiert:

```markdown
# RemNote Plugin Documentation
> Auto-generated index of 150 pages from https://plugins.remnote.com
> All pages have been downloaded locally. Use the local file path instead of crawling the URL.

## API Reference

### Classes
- [Rem](https://plugins.remnote.com/api/classes/Rem): Main Rem object class (local: ./api/classes/Rem/index.md)
- [Query](https://plugins.remnote.com/api/classes/Query): Query builder class (local: ./api/classes/Query/index.md)

### Enums
- [RemType](https://plugins.remnote.com/api/enums/RemType): Rem type enumeration (local: ./api/enums/RemType/index.md)
```

## Sitemap-Modus: Technische Details

### Unterstützte Sitemap-Formate

**Standard Sitemap:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
    <lastmod>2024-01-01</lastmod>
  </url>
  <url>
    <loc>https://example.com/page2</loc>
  </url>
</urlset>
```

**Sitemap-Index:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-part1.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-part2.xml</loc>
  </sitemap>
</sitemapindex>
```

### Verarbeitung

1. **Sitemap Fetching**: HTTP-Request mit `aiohttp`
2. **XML-Parsing**: Verwendung von `xml.etree.ElementTree`
3. **Sitemap-Index-Erkennung**: Automatisch erkannt und rekursiv verarbeitet
4. **URL-Filterung**: Domain- und Präfix-Filter angewendet
5. **Crawling**: Jede URL wird einzeln gecrawlt (depth=1)

### Fehlerbehandlung

- **Sitemap nicht erreichbar**: Fallback zum Normal-Modus
- **Ungültiges XML**: Klare Fehlermeldung
- **Leere Sitemap**: Warnung + Abbruch
- **Einzelne URL-Fehler**: Werden geloggt, Crawling wird fortgesetzt

## Modi-Vergleich

| Feature | Normal-Modus | Sitemap-Modus |
|---------|--------------|---------------|
| URL-Quelle | Link-Following | sitemap.xml |
| Depth | Konfigurierbar | Ignoriert (immer 1) |
| Präfix-Filter | ✅ Unterstützt | ✅ Unterstützt |
| Domain-Filter | ✅ Unterstützt | ✅ Unterstützt |
| Use Case | Explorative Discovery | Vollständige Abdeckung |
| Performance | Abhängig von Depth | Schneller (direkte URLs) |

## Troubleshooting

### "crawl4ai not installed"
```bash
pip install crawl4ai
```

### "aiohttp not installed"
```bash
pip install aiohttp
```

### Keine URLs gefunden im Sitemap-Modus
- Prüfen Sie, ob die URL tatsächlich eine sitemap.xml ist
- Überprüfen Sie die Präfix-Filter-Einstellung
- Testen Sie die Sitemap-URL im Browser

### Timeout-Fehler
- Sitemap ist zu groß oder langsam
- Netzwerkverbindung prüfen
- Timeout-Wert in [`parse_sitemap()`](crawl_docs.py:86) anpassen

## Entwicklung

### Projektstruktur

```
crawl4ai-project/
├── crawl_docs.py              # Haupt-Crawler-Skript
├── requirements.txt           # Python-Abhängigkeiten
├── README.md                  # Diese Datei
├── SITEMAP_FEATURE_PLAN.md   # Technischer Implementierungsplan
└── .venv/                    # Virtuelle Umgebung (nicht im Git)
```

### Neue Features hinzufügen

1. Siehe [`SITEMAP_FEATURE_PLAN.md`](SITEMAP_FEATURE_PLAN.md) für Architektur-Details
2. Funktionen in [`crawl_docs.py`](crawl_docs.py) erweitern
3. Tests durchführen
4. Dokumentation aktualisieren

## Lizenz

[Ihre Lizenz hier einfügen]

## Credits

- Basiert auf [crawl4ai](https://github.com/unclecode/crawl4ai)
- Async HTTP mit [aiohttp](https://github.com/aio-libs/aiohttp)
