from datetime import datetime
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.util import dt as dt_util
from .const import DOMAIN, DOMAINS


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    domain_id = entry.data["domain_id"]
    country_name = DOMAINS.get(domain_id, "Onbekend").split(" - ")[0]

    async_add_entities(
        [
            EntsoeCurrentPriceSensor(coordinator, domain_id, country_name),
            EntsoeLastUpdateSensor(coordinator, domain_id, country_name),
            EntsoeLastUpdateStatusSensor(coordinator, domain_id, country_name),
            EntsoeConsecutiveErrorsSensor(coordinator, domain_id, country_name),
        ]
    )


class EntsoeBaseEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, domain_id, country_name):
        super().__init__(coordinator)
        self._domain_id = domain_id
        self._country_name = country_name
        self._device_id = f"entsoe_{domain_id.lower()}"
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=f"ENTSO-E Energieprijzen ({self._country_name})",
            manufacturer="ENTSO-E",
            model="Transparency Platform API",
        )


class EntsoeCurrentPriceSensor(EntsoeBaseEntity):
    def __init__(self, coordinator, domain_id, country_name):
        super().__init__(coordinator, domain_id, country_name)
        self._attr_translation_key = "current_price"
        self._attr_unique_id = f"{self._device_id}_current_price"
        self._attr_icon = "mdi:flash"
        self._attr_native_unit_of_measurement = "EUR/kWh"

    @property
    def state(self):
        if not self.coordinator.data:
            return None

        now_utc = dt_util.utcnow()

        # Loop door de lijst en zoek het actuele tijdvak. Omdat we niet exact de lengte
        # van het tijdvak weten (15m of 60m), zoeken we de laatste timestamp in het
        # verleden, aannemende dat dat het huidige blok is.
        current_price = None
        for item in self.coordinator.data:
            try:
                item_time = datetime.fromisoformat(item["timestamp_utc"])
                if item_time <= now_utc:
                    current_price = item["price_kwh"]
                else:
                    break  # We zijn de huidige tijd voorbij, stop met zoeken
            except Exception:
                continue

        return current_price

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        # Geef de volledige dataset mee zodat je in Markdown grafieken kunt bouwen
        return {"all_prices": self.coordinator.data}


class EntsoeLastUpdateSensor(EntsoeBaseEntity):
    def __init__(self, coordinator, domain_id, country_name):
        super().__init__(coordinator, domain_id, country_name)
        self._attr_translation_key = "last_update"
        self._attr_unique_id = f"{self._device_id}_last_update"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:clock-outline"

    @property
    def state(self):
        if (
            hasattr(self.coordinator, "last_update_success_timestamp")
            and self.coordinator.last_update_success_timestamp
        ):
            return self.coordinator.last_update_success_timestamp
        return None


class EntsoeLastUpdateStatusSensor(EntsoeBaseEntity):
    def __init__(self, coordinator, domain_id, country_name):
        super().__init__(coordinator, domain_id, country_name)
        self._attr_translation_key = "last_status"
        self._attr_unique_id = f"{self._device_id}_last_status"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:eye-check"

    @property
    def state(self):
        return (
            "Success" if getattr(self.coordinator, "error_count", 0) == 0 else "Error"
        )


class EntsoeConsecutiveErrorsSensor(EntsoeBaseEntity):
    def __init__(self, coordinator, domain_id, country_name):
        super().__init__(coordinator, domain_id, country_name)
        self._attr_translation_key = "errors"
        self._attr_unique_id = f"{self._device_id}_errors"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:alert-circle-outline"

    @property
    def state(self):
        return getattr(self.coordinator, "error_count", 0)
