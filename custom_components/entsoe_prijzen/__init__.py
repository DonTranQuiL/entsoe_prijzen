import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, PLATFORMS
from .coordinator import EntsoeCoordinator
from .cache import EntsoeCache

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    cache_module = EntsoeCache(hass, entry.data["domain_id"])
    coordinator = EntsoeCoordinator(hass, entry, cache_module)
    
    # Laad de cache razendsnel in tijdens opstarten
    coordinator.last_data = await hass.async_add_executor_job(cache_module.load_cache)
    
    if coordinator.last_data:
        coordinator.data = coordinator.last_data
        entry.async_create_background_task(hass, coordinator.async_request_refresh(), "entsoe_bg_refresh")
    else:
        await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async def handle_refresh(call: ServiceCall):
        for coord in hass.data[DOMAIN].values():
            await coord.async_request_refresh()

    async def handle_clear_files(call: ServiceCall):
        for entry_id, coord in hass.data[DOMAIN].items():
            await hass.async_add_executor_job(coord.cache.clear_cache)
            # Ook debug files opschonen, vereist even wat pad-logica
            import os
            debug_path = os.path.join(os.path.dirname(__file__), f"entsoe_debug_{coord.domain_id}.txt")
            if os.path.exists(debug_path):
                try: 
                    os.remove(debug_path)
                except Exception: 
                    pass

    hass.services.async_register(DOMAIN, "refresh", handle_refresh)
    hass.services.async_register(DOMAIN, "clear_files", handle_clear_files)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
