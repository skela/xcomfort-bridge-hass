import asyncio
import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_AUTH_KEY,DOMAIN,PLATFORMS,CONF_IDENTIFIER

from .hub import XComfortHub

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
	hass.data.setdefault(DOMAIN, {})
	return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

	config = entry.data
	identifier = config.get(CONF_IDENTIFIER)
	ip = config.get(CONF_IP_ADDRESS)
	auth_key = config.get(CONF_AUTH_KEY)

	hub = XComfortHub(hass,identifier=identifier,ip=ip,auth_key=auth_key)
	hub.start()	
	hass.data[DOMAIN][entry.entry_id] = hub

	await hub.load_devices()

	for platform in PLATFORMS:
		hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, platform))

	return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
	
	hub = XComfortHub.get_hub(hass,entry)
	await hub.stop()

	unload_ok = all(
		await asyncio.gather(
			*[
				hass.config_entries.async_forward_entry_unload(
					entry, platform)
				for platform in PLATFORMS
			]
		)
	)
	if unload_ok:
		hass.data[DOMAIN].pop(entry.entry_id)

	return unload_ok
