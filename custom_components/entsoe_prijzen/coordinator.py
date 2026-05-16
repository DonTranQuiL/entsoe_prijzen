import asyncio
import os
import xml.etree.ElementTree as ET
from datetime import timedelta, datetime
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_API_TOKEN, CONF_DOMAIN_ID

_LOGGER = logging.getLogger(__name__)

class EntsoeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config_entry, cache_module):
        self.hass = hass
        self.api_token = config_entry.data[CONF_API_TOKEN]
        self.domain_id = config_entry.data[CONF_DOMAIN_ID]
        self.cache = cache_module
        
        self.last_data = [] 
        self.error_count = 0
        self.last_update_success_timestamp = None
        self._is_first_run = True
        
        scan_interval = config_entry.options.get("scan_interval", 3600)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=scan_interval))

    def _write_debug_file_sync(self, debug_path, content):
        try:
            with open(debug_path, "w", encoding="utf-8") as f: 
                f.write(content)
        except Exception:
            pass

    async def _async_update_data(self):
        if self._is_first_run and self.last_data:
            self._is_first_run = False
            _LOGGER.debug("Eerste run: ENTSO-E Download overgeslagen, cache gebruikt.")
            return self.last_data
            
        self._is_first_run = False
        session = async_get_clientsession(self.hass)
        
        # ENTSO-E verwacht de datums in UTC als YYYYMMDDHH00
        # We pakken gisteren om 22:00 UTC (00:00 lokaal) tot morgen 22:00 UTC
        now_utc = dt_util.utcnow()
        start_time = (now_utc - timedelta(days=1)).replace(hour=22, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=3)
        
        period_start = start_time.strftime("%Y%m%d%H00")
        period_end = end_time.strftime("%Y%m%d%H00")
        
        url = f"https://web-api.tp.entsoe.eu/api?securityToken={self.api_token}&documentType=A44&in_Domain={self.domain_id}&out_Domain={self.domain_id}&periodStart={period_start}&periodEnd={period_end}"
        debug_log_content = f"ENTSO-E DEBUG LOG\nURL: {url}\n\n"
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    _LOGGER.error("ENTSO-E API fout: %s", response.status)
                    self.error_count += 1
                    return self.last_data
                
                xml_data = await response.text()
                
                # Verwijder XML namespaces
                root = ET.fromstring(xml_data)
                for elem in root.iter():
                    if '}' in elem.tag: 
                        elem.tag = elem.tag.split('}', 1)[1]

                prices = []
                for timeseries in root.findall('.//TimeSeries'):
                    period = timeseries.find('.//Period')
                    if period is None:
                        continue
                    
                    # Bepaal resolutie (PT15M = 15 min, PT60M = 60 min)
                    res_str = period.findtext('resolution', 'PT60M')
                    delta = timedelta(hours=1)
                    if res_str == 'PT15M': 
                        delta = timedelta(minutes=15)
                    elif res_str == 'PT30M': 
                        delta = timedelta(minutes=30)
                    
                    start_str = period.findtext('.//timeInterval/start')
                    if not start_str:
                        continue
                    
                    try:
                        base_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    except Exception:
                        continue

                    for point in period.findall('.//Point'):
                        pos_str = point.findtext('position')
                        price_str = point.findtext('price.amount')
                        if not pos_str or not price_str:
                            continue
                        
                        pos = int(pos_str)
                        price_mwh = float(price_str)
                        # Omrekenen naar EUR/kWh met 5 decimalen achter de komma
                        price_kwh = round(price_mwh / 1000, 5) 
                        
                        point_time = base_time + (pos - 1) * delta
                        
                        prices.append({
                            "timestamp_utc": point_time.isoformat(),
                            "price_mwh": price_mwh,
                            "price_kwh": price_kwh
                        })

                # Sorteer op tijdstip
                prices.sort(key=lambda x: x["timestamp_utc"])
                
                # Filter dubbele eruit (soms stuurt ENTSO-E overlappende blokken)
                unique_prices = []
                seen_times = set()
                for p in prices:
                    if p["timestamp_utc"] not in seen_times:
                        seen_times.add(p["timestamp_utc"])
                        unique_prices.append(p)

            if unique_prices:
                self.last_data = unique_prices
                await self.hass.async_add_executor_job(self.cache.save_cache, unique_prices)
                self.error_count = 0
                self.last_update_success_timestamp = dt_util.utcnow()
            else:
                self.error_count += 1
                
            current_dir = os.path.dirname(__file__)
            debug_path = os.path.join(current_dir, f"entsoe_debug_{self.domain_id}.txt")
            await self.hass.async_add_executor_job(self._write_debug_file_sync, debug_path, debug_log_content)
            
            return self.last_data
            
        except Exception as err:
            self.error_count += 1
            _LOGGER.error("Update mislukt voor ENTSO-E: %s", err)
            return self.last_data
