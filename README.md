# Universal Documentation Crawler

Ein leistungsstarker Python-basierter Web-Crawler, der Dokumentations-Websites crawlt und als saubere, LLM-optimierte Markdown-Dateien speichert.

## Features

✅ **Drei Crawl-Modi:**
- **Normal-Modus**: Folgt Links auf der Website bis zu einer konfigurierbaren Tiefe (BFS-Strategie)
- **Sitemap-URL-Modus**: Parst `sitemap.xml` von einer URL und crawlt alle aufgelisteten URLs direkt
- **Sitemap-File-Modus**: Parst lokale `sitemap.xml` Datei und crawlt alle aufgelisteten URLs

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

### Sitemap-URL-Modus

```bash
# Sitemap von URL parsen und alle URLs crawlen
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap

# Sitemap mit Präfix-Filter (nur URLs die mit /docs beginnen)
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap --prefix /docs

# Sitemap mit llms.txt Index
python crawl_docs.py --url https://example.com/sitemap.xml --from-sitemap --llms-txt
```

**Hinweis:** Im Sitemap-URL-Modus wird die `--depth` Option ignoriert, da alle URLs direkt aus der Sitemap extrahiert werden.

### Sitemap-File-Modus

```bash
# Lokale Sitemap-Datei parsen und crawlen
python crawl_docs.py --sitemap-file ./sitemap.xml

# Mit expliziter Base-URL (für Domain-Filter und Dateipfad-Generierung)
python crawl_docs.py --sitemap-file ./sitemap.xml --url https://example.com

# Mit Präfix-Filter (nur URLs die mit /docs beginnen)
python crawl_docs.py --sitemap-file ./sitemap.xml --prefix /docs

# Mit llms.txt Index-Generierung
python crawl_docs.py --sitemap-file ./sitemap.xml --llms-txt

# Vollständiges Beispiel mit allen Optionen
python crawl_docs.py --sitemap-file ./my-sitemap.xml --url https://example.com --prefix /api --out ./api-docs --llms-txt
```

**Besonderheiten des Sitemap-File-Modus:**
- `--url` ist **optional**. Wenn nicht gesetzt, wird die Domain automatisch aus der ersten URL in der Sitemap erkannt
- Domain-Filter wird **nur** angewendet wenn `--url` explizit gesetzt ist
- Unterstützt Sitemap-Index-Dateien (Sub-Sitemaps werden automatisch via HTTP geladen)
- Die `--depth` Option wird ignoriert
- **Nicht kombinierbar** mit `--from-sitemap`

### Alle Optionen

```
--url URL              Start-URL zum Crawlen (optional bei --sitemap-file)
--prefix PREFIX        Nur URLs mit diesem Pfad-Präfix crawlen
--depth DEPTH          Maximale Crawl-Tiefe (Standard: 5, ignoriert bei Sitemap-Modi)
--out OUTPUT_DIR       Output-Verzeichnis (Standard: ./docs)
--exclude SELECTORS    CSS-Selektoren zum Entfernen (z.B. "nav, footer")
--llms-txt             llms.txt Index-Datei generieren
--from-sitemap         Sitemap-URL-Modus aktivieren (parst sitemap.xml von URL)
--sitemap-file PATH    Sitemap-File-Modus aktivieren (parst lokale sitemap.xml Datei)
```

**Hinweis:** `--from-sitemap` und `--sitemap-file` können nicht zusammen verwendet werden.

## Konfiguration

Die Standard-Konfiguration kann in [`crawl_docs.py`](crawl_docs.py:24) angepasst werden:

```python
CONFIG = {
    "url": "",
    "url_prefix": "",
    "max_depth": 5,
    "output_dir": "./docs",
    "excluded_selectors": "nav, footer, .sidebar, .navbar, header, .toc, [role='navigation']",
    "generate_llms_txt": True,
    "from_sitemap": False,
    "sitemap_file": "",
}
```

## Beispiele

### Beispiel 1: RemNote Plugin Dokumentation (Sitemap-URL)

```bash
python crawl_docs.py --url https://plugins.remnote.com/sitemap.xml --from-sitemap --llms-txt
```

### Beispiel 2: Lokale Sitemap-Datei verwenden

```bash
python crawl_docs.py --sitemap-file ./my-sitemap.xml --llms-txt
```

### Beispiel 3: Lokale Sitemap mit expliziter Base-URL

```bash
python crawl_docs.py --sitemap-file ./sitemap.xml --url https://example.com --prefix /docs
```

### Beispiel 4: Nur API-Dokumentation crawlen (Normal-Modus)

```bash
python crawl_docs.py --url https://docs.example.com --prefix /api/v2 --depth 3
```

### Beispiel 5: Mehrere Sitemaps (Sitemap-Index)

```bash
# Von URL
python crawl_docs.py --url https://example.com/sitemap_index.xml --from-sitemap

# Von lokaler Datei
python crawl_docs.py --sitemap-file ./sitemap_index.xml
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

## Sitemap-Modi: Technische Details

Beide Sitemap-Modi (URL und File) unterstützen die gleichen XML-Formate und verwenden die gleiche Parsing-Logik.

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

**Sitemap-URL-Modus (`--from-sitemap`):**
1. **Sitemap Fetching**: HTTP-Request mit `aiohttp`
2. **XML-Parsing**: Verwendung von `xml.etree.ElementTree` (via `_parse_sitemap_xml()`)
3. **Sitemap-Index-Erkennung**: Automatisch erkannt und Sub-Sitemaps rekursiv via HTTP geladen
4. **URL-Filterung**: Domain- und Präfix-Filter angewendet
5. **Crawling**: Jede URL wird einzeln gecrawlt

**Sitemap-File-Modus (`--sitemap-file`):**
1. **Datei Lesen**: Lokale XML-Datei von Disk einlesen
2. **XML-Parsing**: Verwendung von `xml.etree.ElementTree` (via `_parse_sitemap_xml()`)
3. **Sitemap-Index-Erkennung**: Automatisch erkannt, Sub-Sitemaps werden via HTTP geladen
4. **URL-Filterung**: Präfix-Filter immer, Domain-Filter nur bei `--url`
5. **Crawling**: Jede URL wird einzeln gecrawlt

### Fehlerbehandlung

- **Sitemap nicht erreichbar**: Fallback zum Normal-Modus
- **Ungültiges XML**: Klare Fehlermeldung
- **Leere Sitemap**: Warnung + Abbruch
- **Einzelne URL-Fehler**: Werden geloggt, Crawling wird fortgesetzt

## Modi-Vergleich

| Feature | Normal-Modus | Sitemap-URL-Modus | Sitemap-File-Modus |
|---------|--------------|-------------------|-------------------|
| URL-Quelle | Link-Following | sitemap.xml (URL) | sitemap.xml (lokal) |
| Depth | Konfigurierbar | Ignoriert | Ignoriert |
| Präfix-Filter | ✅ Unterstützt | ✅ Unterstützt | ✅ Unterstützt |
| Domain-Filter | ✅ Immer aktiv | ✅ Immer aktiv | ⚡ Nur bei `--url` |
| Base-URL | Erforderlich (`--url`) | Erforderlich (`--url`) | Optional (auto-detect) |
| Use Case | Explorative Discovery | Vollständige Abdeckung | Offline/Lokal |
| Performance | Abhängig von Depth | Schnell (direkte URLs) | Schnell (direkte URLs) |
| Sitemap-Index | N/A | ✅ Unterstützt | ✅ Unterstützt |

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
