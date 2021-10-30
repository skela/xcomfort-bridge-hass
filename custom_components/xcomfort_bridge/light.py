import asyncio

import logging
from math import ceil
from homeassistant.config_entries import ConfigEntry

from xcomfort import Bridge
from xcomfort.bridge import State
from xcomfort.devices import LightState,Light

from homeassistant.components.light import (ATTR_BRIGHTNESS,SUPPORT_BRIGHTNESS,LightEntity)

from .hub import XComfortHub
from .const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
# 	vol.Required(CONF_IP_ADDRESS): cv.string,
# 	vol.Required(CONF_AUTH_KEY): cv.string,
# })

async def async_setup_entry(hass:HomeAssistant,entry:ConfigEntry,async_add_entities:AddEntitiesCallback):

	hub = XComfortHub.get_hub(hass,entry)

	devices = hub.devices

	_LOGGER.info(f"Found {len(devices)} xcomfort devices")

	lights = list()
	for device in devices:
		
		_LOGGER.info(f"Adding {device}")
		light = HASSXComfortLight(hass, hub, device)
		lights.append(light)

	_LOGGER.info(f"Added {len(lights)} lights")
	async_add_entities(lights, True)

class HASSXComfortLight(LightEntity):
	
	def __init__(self,hass:HomeAssistant,hub:XComfortHub,device:Light):
		self.hass = hass
		self.hub = hub

		self._device = device
		self._name = device.name
		self._state = None
		
		self._unique_id = f"light_{DOMAIN}_{hub.identifier}-{device.device_id}"
		self._device.state.subscribe(self._state_change)

	def _state_change(self, state):
		update = self._state is not None
		self._state = state

		_LOGGER.info(f"State changed {self._name} : {state}")

		if update:
			self.schedule_update_ha_state()

	@property
	def device_info(self):
		return {
			"identifiers": {				
				(DOMAIN, self.unique_id)
			},
			"name": self.name,
			"manufacturer": "Eaton",
			"model": "XXX",
			"sw_version": "1.0.0",
			"via_device": self.hub.hub_id,
		}

	@property
	def name(self):
		"""Return the display name of this light."""
		return self._name

	@property
	def unique_id(self):
		"""Return the unique ID."""
		return self._unique_id

	@property
	def should_poll(self) -> bool:
		return False

	@property
	def brightness(self):
		"""Return the brightness of the light.

		This method is optional. Removing it indicates to Home Assistant
		that brightness is not supported for this light.
		"""
		return int(255.0 * self._state.dimmvalue / 99.0)

	@property
	def is_on(self):
		"""Return true if light is on."""
		return self._state.switch

	@property
	def supported_features(self):
		"""Flag supported features."""
		if self._device.dimmable:
			return SUPPORT_BRIGHTNESS
		return 0

	async def async_turn_on(self, **kwargs):
		"""Instruct the light to turn on."""
		if ATTR_BRIGHTNESS in kwargs and self._device.dimmable:
			# Convert Home Assistant brightness (0-255) to Abode brightness (0-99)
			# If 100 is sent to Abode, response is 99 causing an error
			await self._device.dimm(ceil(kwargs[ATTR_BRIGHTNESS] * 99 / 255.0))
			return

		switch_task = self._device.switch(True)
		self._state.switch = True
		self.schedule_update_ha_state()

		await switch_task

	async def async_turn_off(self, **kwargs):
		"""Instruct the light to turn off."""
		switch_task = self._device.switch(False)
		self._state.switch = False
		self.schedule_update_ha_state()

		await switch_task

	def update(self):
		pass

