<div align="center">
  
# ⚡ ENTSO-E Energieprijzen voor Home Assistant

</div>

<p align="center">
  <!-- Release / License -->
  <a href="https://github.com/DonTranQuiL/entsoe_prijzen/releases">
    <img src="https://img.shields.io/github/v/release/DonTranQuiL/entsoe_prijzen?style=for-the-badge&color=007ec6" alt="Latest Release">
  </a>
  <a href="https://github.com/DonTranQuiL/entsoe_prijzen/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/DonTranQuiL/entsoe_prijzen?style=for-the-badge&color=007ec6" alt="License">
  </a>

  <!-- CI / Quality -->
  <a href="https://github.com/DonTranQuiL/entsoe_prijzen/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DonTranQuiL/entsoe_prijzen/codechecker.yml?style=for-the-badge&label=CODE%20CHECKS&color=5dbb0f" alt="Code Checks">
  </a>
  <a href="https://github.com/DonTranQuiL/entsoe_prijzen/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DonTranQuiL/entsoe_prijzen/pytest.yml?style=for-the-badge&label=TESTS&color=5dbb0f" alt="Tests">
  </a>
  <a href="https://github.com/DonTranQuiL/entsoe_prijzen/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/DonTranQuiL/entsoe_prijzen/hacs.yaml?style=for-the-badge&label=HACS%20VALIDATION&color=5dbb0f" alt="HACS Validation">
  </a>

  <!-- Code Quality -->
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-5dbb0f?style=for-the-badge" alt="pre-commit">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/badge/code%20style-ruff-000000?style=for-the-badge" alt="Ruff">
  </a>
  <a href="https://codecov.io/gh/DonTranQuiL/entsoe_prijzen">
  <img 
    src="https://codecov.io/gh/DonTranQuiL/entsoe_prijzen/branch/main/graph/badge.svg"
    alt="Coverage"
    style="height:28px;"
  >
</a>

  <!-- Ecosystem -->
  <a href="https://hacs.xyz/">
    <img src="https://img.shields.io/badge/HACS-CUSTOM-ff6e27?style=for-the-badge" alt="HACS">
  </a>
  <a href="https://www.home-assistant.io/">
    <img src="https://img.shields.io/badge/Home%20Assistant-2024.5%2B-007ec6?style=for-the-badge" alt="Home Assistant">
  </a>

  <!-- Social / Support -->
  <a href="https://github.com/DonTranQuiL">
    <img src="https://img.shields.io/badge/maintainer-%40DonTranQuiL-007ec6?style=for-the-badge" alt="Maintainer">
  </a>
  <a href="https://ko-fi.com/DonTranQuiL">
    <img src="https://img.shields.io/badge/buy%20me%20a%20coffee-donate-ffdd00?style=for-the-badge" alt="Donate">
  </a>
  <a href="https://community.home-assistant.io/">
    <img src="https://img.shields.io/badge/community-forum-007ec6?style=for-the-badge" alt="Community">
  </a>
</p>

</div>

<div align="center">

Een efficiënte, razendsnelle en robuuste Home Assistant integratie die de officiële Day-Ahead elektriciteitsprijzen ophaalt via het Europese ENTSO-E Transparency Platform. Ideaal voor het automatiseren van grootverbruikers (zoals laadpalen en warmtepompen) op basis van dynamische stroomprijzen.

</div>

## ✨ Functionaliteiten

* **Smart Cache Booting:** Laadt data na een herstart direct in vanaf de lokale schijf. Home Assistant hoeft niet te wachten op de ENTSO-E API, wat zorgt voor een bliksemsnelle opstarttijd.
* **Automatische Omrekening:** Rekent de complexe ENTSO-E data (EUR/MWh) automatisch om naar leesbare consumentenprijzen (EUR/kWh).
* **Europese Dekking:** Ondersteunt diverse biedingszones/landen (NL, BE, DE, FR, GB, GR, IT) met de juiste resoluties (15 of 60 minuten).
* **Toekomstgericht:** Haalt rond 14:00 uur automatisch de prijzen voor de volgende dag op.
* **Geoptimaliseerd:** Achtergrondverwerking blokkeert je Home Assistant systeem niet.

## 📥 Installatie via HACS

1. Ga in Home Assistant naar **HACS** > **Integraties**.
2. Klik rechtsboven op de drie puntjes en kies **Aangepaste repositories** (Custom repositories).
3. Voeg de URL van deze repository toe en kies als categorie **Integratie**.
4. Klik op toevoegen, zoek naar *ENTSO-E Energieprijzen* in HACS en klik op **Download**.
5. Herstart Home Assistant.

## ⚙️ Configuratie

1. Maak een gratis account aan op [transparency.entsoe.eu](https://transparency.entsoe.eu/) en vraag een Security Token aan door hun te meailen.
2. Ga in Home Assistant naar **Instellingen** > **Apparaten & Diensten**.
3. Klik rechtsonder op **+ Integratie toevoegen**.
4. Zoek naar **ENTSO-E Energieprijzen**.
5. Vul je API Token in en selecteer je land/biedingszone.

## 📊 Dashboard Kaart (Markdown)

Gebruik deze code in een Markdown-kaart voor een prachtig, dynamisch overzicht dat je actuele prijs in centen toont, inclusief een handig tabelletje voor de komende uren.

```yaml
type: markdown
content: >-
  {% set entity = 'sensor.entso_e_energieprijzen_nl_current_price' %} {% set
  prices = state_attr(entity, 'all_prices') %}

  ## ⚡ Actuele Stroomprijs (Day-Ahead)

  {% if prices %} {% set current_price_eur = states(entity) | float(0) %}

  {# Formatteer de prijs mooi naar Euro's met 2 decimalen achter de komma (bijv.
  0,10) #} {% set format_price = "{:0.2f}".format(current_price_eur) |
  replace('.', ',') %}

  {% set color_main = '#00C853' %} {% set advies = 'Prijzen zijn zeer laag (of
  zelfs negatief). Perfect moment om wasmachines, drogers of laders aan te
  zetten!' %} {% set icon = '🔥' %}

  {% if current_price_eur > 0 %}
    {% set color_main = '#8BC34A' %}
    {% set advies = 'Prijzen zijn gunstig. Een prima moment voor stroomverbruik.' %}
    {% set icon = '✅' %}
  {% endif %}

  {% if current_price_eur > 0.08 %}
    {% set color_main = '#FF9800' %}
    {% set advies = 'Prijzen zijn gemiddeld. Geen bijzonderheden.' %}
    {% set icon = '⚖️' %}
  {% endif %}

  {% if current_price_eur > 0.15 %}
    {% set color_main = '#F44336' %}
    {% set advies = 'Prijzen zijn hoog! Stel grote stroomverbruikers even uit als dat mogelijk is.' %}
    {% set icon = '⚠️' %}
  {% endif %}

  <div style="background-color: rgba(128, 128, 128, 0.1); padding: 20px;
  border-radius: 10px; text-align: center; margin-bottom: 15px;"> <div
  style="font-size: 1.2em; opacity: 0.8;">Huidig Uurtarief</div> <div
  style="font-size: 3em; font-weight: bold; color: {{ color_main }};
  line-height: 1.1;"> &euro; {{ format_price }} </div> <div style="font-size:
  0.85em; opacity: 0.6; margin-top: 5px;"> Kale inkoopprijs per kWh (excl. btw &
  opslag) </div> </div>

  <div style="background-color: {{ color_main }}15; padding: 15px; border-left:
  5px solid {{ color_main }}; border-radius: 5px; margin-bottom: 20px;"> <b>{{
  icon }} Advies voor dit uur:</b><br>{{ advies }} </div>

  <br>

  🕒 Verwachte prijzen (komende 8 uur) <table style="width: 100%;
  text-align: left; border-collapse: collapse; font-size: 0.95em;"> <tr> <th
  style="border-bottom: 1px solid rgba(128, 128, 128, 0.3); padding: 8px
  0;">Tijd</th> <th style="border-bottom: 1px solid rgba(128, 128, 128, 0.3);
  padding: 8px 0;">Prijs (per kWh)</th> </tr> {% set ns = namespace(found=0) %}
  {% for item in prices %} {% set item_time = as_datetime(item.timestamp_utc) |
  as_local %} {% if item_time >= now().replace(minute=0, second=0,
  microsecond=0) and item_time.minute == 0 and ns.found < 8 %} {% set
  format_item = "{:0.2f}".format(item.price_kwh) | replace('.', ',') %} {% set
  color = '#00C853' %} {% if item.price_kwh > 0 %}{% set color = '#8BC34A' %}{%
  endif %} {% if item.price_kwh > 0.08 %}{% set color = '#FF9800' %}{% endif %}
  {% if item.price_kwh > 0.15 %}{% set color = '#F44336' %}{% endif %}

  {% set time_str = item_time.strftime('%H:%M') %} {% if item_time.day !=
  now().day %}
    {% set time_str = 'Morgen ' ~ item_time.strftime('%H:%M') %}
  {% endif %}

  <tr> <td style="padding: 8px 0;">{{ time_str }}</td> <td style="padding: 8px
  0; color: {{ color }}; font-weight: bold;">&euro; {{ format_item }}</td> </tr>
  {% set ns.found = ns.found + 1 %} {% endif %} {% endfor %} </table>

  <br>  <br>

  📅 Prijzen voor Morgen {% set tomorrow = (now() + timedelta(days=1)).day
  %} {% set ns_morgen = namespace(found=0) %}

  {# Check eerst of er prijzen voor morgen zijn #} {% for item in prices %} {%
  set item_time = as_datetime(item.timestamp_utc) | as_local %} {% if
  item_time.day == tomorrow %} {% set ns_morgen.found = 1 %} {% endif %} {%
  endfor %}

  {% if ns_morgen.found == 1 %} <table style="width: 100%; text-align: left;
  border-collapse: collapse; font-size: 0.95em;"> <tr> <th style="border-bottom:
  1px solid rgba(128, 128, 128, 0.3); padding: 8px 0;">Tijd</th> <th
  style="border-bottom: 1px solid rgba(128, 128, 128, 0.3); padding: 8px
  0;">Prijs (per kWh)</th> </tr> {% for item in prices %} {% set item_time =
  as_datetime(item.timestamp_utc) | as_local %} {% if item_time.day == tomorrow
  and item_time.minute == 0 %} {% set format_item =
  "{:0.2f}".format(item.price_kwh) | replace('.', ',') %} {% set color =
  '#00C853' %} {% if item.price_kwh > 0 %}{% set color = '#8BC34A' %}{% endif %}
  {% if item.price_kwh > 0.08 %}{% set color = '#FF9800' %}{% endif %} {% if
  item.price_kwh > 0.15 %}{% set color = '#F44336' %}{% endif %} <tr> <td
  style="padding: 8px 0;">{{ item_time.strftime('%H:%M') }}</td> <td
  style="padding: 8px 0; color: {{ color }}; font-weight: bold;">&euro; {{
  format_item }}</td> </tr> {% endif %} {% endfor %} </table> {% else %} <div
  style="opacity: 0.7; font-style: italic; padding: 10px 0;"> De prijzen voor
  morgen zijn nog niet bekend. Deze worden doorgaans tussen 13:00 en 14:00 uur
  gepubliceerd. </div> {% endif %}

  {% else %} ⏳ Data wordt nog geladen... {% endif %}

```
<img width="504" height="747" alt="{A1B9F634-537C-44C2-A797-697F810510F4}" src="https://github.com/user-attachments/assets/2ff18ea7-6b0c-43a6-b899-5ac4b4118ccc" />

