# DHL Paket Tracker (Home Assistant Custom Integration)

Diese Integration bindet die DHL-Paket-Tracking-API in Home Assistant ein und erstellt pro Sendungsnummer einen Sensor.

## Features

- Konfiguration komplett über UI (Config Flow)
- Mehrere Sendungsnummern pro Integrationseintrag
- Polling-Intervall konfigurierbar (5 bis 720 Minuten)
- Relevante Paketdetails als Sensor-Attribute (Status, Events, Ziel, ETA)
- HACS-kompatibel

## Installation über HACS (Custom Repository)

1. HACS öffnen
2. **Integrations** → Menü (⋮) → **Custom repositories**
3. URL dieses Repositories eintragen
4. Kategorie: **Integration**
5. Integration installieren
6. Home Assistant neu starten

## Einrichtung

1. In Home Assistant: **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**
2. Nach **DHL Paket Tracker** suchen
3. Schritt 1: DHL API Key eintragen
4. Schritt 1: Optional API Secret eintragen (falls dein DHL-Produkt es verlangt)
5. Schritt 2: Eine oder mehrere Sendungsnummern eintragen (Komma oder neue Zeile)
6. Speichern

## Hinweise zur API

Diese Integration nutzt den DHL-Tracking-Endpunkt unter:

- `https://api-eu.dhl.com/track/shipments?trackingNumber=<NUMMER>`

Der API-Key wird als Header `DHL-API-Key` gesendet.

Wenn ein API-Secret hinterlegt ist, sendet die Integration zusätzlich:

- `Authorization: Basic <base64(api_key:api_secret)>`
- `DHL-API-Secret: <api_secret>`

## Entitäten

Pro Tracking-Nummer wird ein Sensor erstellt, z. B.:

- `sensor.sendung_123456`

**State:** aktueller Versandstatus

**Attribute (Auszug):**

- `tracking_number`
- `status_code`
- `status_description`
- `estimated_delivery`
- `origin`
- `destination`
- `events` (max. 10 letzte Events)

## Disclaimer

Die DHL-API kann je nach Vertrag/Produkt andere Felder oder Auth-Anforderungen haben. Falls dein Endpoint andere Header oder OAuth voraussetzt, kann die Integration entsprechend erweitert werden.

## Troubleshooting

- Wenn beim Einrichten weiterhin `invalid_auth` erscheint, prüfe bitte, ob dein DHL-Produkt zusätzlich ein API-Secret verlangt und trage es im Config-Flow ein.
- Bei produkt-/sendungsspezifischen API-Fehlern kann der Setup-Test fehlschlagen, obwohl der Key korrekt ist. Die Integration legt den Eintrag trotzdem an und versucht den Abruf danach zyklisch erneut.

- Hinweis: Konfigurationsdialoge werden von Home Assistant teilweise gecacht. Nach einem Integrations-Update ggf. Home Assistant neu starten, damit neue Felder (z. B. API-Secret) sicher angezeigt werden.
