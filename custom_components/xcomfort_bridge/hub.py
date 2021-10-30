
from __future__ import annotations
import asyncio
import logging
from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from .const import DOMAIN

from xcomfort.bridge import Bridge, State
from xcomfort.devices import Light, LightState

_LOGGER = logging.getLogger(__name__)

class XComfortHub(object):

	def __init__(self,hass:HomeAssistant,identifier:str,ip:str,auth_key:str):

		bridge = XComfortBridge(ip, auth_key)
		self.bridge = bridge
		self.identifier = identifier
		if self.identifier is None:
			self.identifier = ip
		self._id = ip
		self.devices = list()
		_LOGGER.warning("getting event loop")
		self._loop = asyncio.get_event_loop()

	def start(self):
		_LOGGER.warning("run bridge")
		# hass.create_task(bridge.run())
		asyncio.create_task(self.bridge.run())
		_LOGGER.warning("ran bridge")

	async def stop(self):
		await self.bridge.close()

	async def load_devices(self):
		_LOGGER.warning("loading devices")
		devs = await self.bridge.get_devices()
		self.devices = devs.values()
		_LOGGER.warning(f"loaded {len(self.devices)} devices")

	@property
	def hub_id(self) -> str:		
		return self._id

	async def test_connection(self) -> bool:		
		await asyncio.sleep(1)
		return True
	
	@staticmethod
	def get_hub(hass:HomeAssistant,entry:ConfigEntry) -> XComfortHub:
		return hass.data[DOMAIN][entry.entry_id]


class XComfortBridge(Bridge):

	def __init__(self, ip_address:str, authkey:str, session = None):
		super().__init__(ip_address, authkey, session)

	def _handle_SET_ALL_DATA(self, payload):
		
		if 'lastItem' in payload:
			self.state = State.Ready
		
		if 'devices' in payload:
			for device in payload['devices']:
				device_id = device['deviceId']
				name = device['name']
				dev_type = device["devType"]

				if dev_type == 100 or dev_type == 101:
					dimmable = device['dimmable']
					state = LightState(device['switch'], device['dimmvalue'])
					light = Light(self, device_id, name, dimmable, state)
					self._add_device(light)
				else:
					_LOGGER.warning(f"Unknown device type {dev_type} named '{name}' - Skipped")
