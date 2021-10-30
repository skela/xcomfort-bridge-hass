"""Config flow for Eaton xComfort Bridge."""
import logging
from typing import List, Optional

import voluptuous as vol
from aiohttp import ClientConnectionError
from homeassistant import config_entries
from homeassistant.const import CONF_MONITORED_CONDITIONS, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from homeassistant.const import CONF_IP_ADDRESS

from .const import DOMAIN,CONF_AUTH_KEY,CONF_IDENTIFIER

_LOGGER = logging.getLogger(__name__)

# CONFIG_SCHEMA = vol.Schema(
# 	{
# 		DOMAIN: vol.All(
# 			cv.ensure_list,
# 			[
# 				vol.Schema(
# 					{
# 						vol.Required(CONF_IP_ADDRESS): cv.string,
# 						vol.Required(CONF_AUTH_KEY): cv.string,
# 						vol.Optional(CONF_IDENTIFIER, default=None): cv.string,
# 					}
# 				),
# 			],			
# 		)
# 	},
# 	extra=vol.ALLOW_EXTRA,
# )

@config_entries.HANDLERS.register(DOMAIN)
class XComfortBridgeConfigFlow(config_entries.ConfigFlow):
	
	VERSION = 1
	CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_PUSH

	def __init__(self):
		self.data = {}
		
	async def async_step_user(self, user_input=None):
		
		entries = self.hass.config_entries.async_entries(DOMAIN)
		if entries:
			return self.async_abort(reason="already_setup")

		errors = {}

		if user_input is not None:

			self.data[CONF_IP_ADDRESS] = user_input[CONF_IP_ADDRESS]
			self.data[CONF_AUTH_KEY] = user_input[CONF_AUTH_KEY]
			self.data[CONF_IDENTIFIER] = user_input.get(CONF_IDENTIFIER)
			
			await self.async_set_unique_id(self.data[CONF_IP_ADDRESS])

			return self.async_create_entry(title=f"{user_input[CONF_IP_ADDRESS]}",data=user_input,)

		data_schema = {
			vol.Required(CONF_IP_ADDRESS): str,
			vol.Required(CONF_AUTH_KEY): str,
			vol.Optional(CONF_IDENTIFIER, default=None): str,
		}

		return self.async_show_form(step_id="user",data_schema=vol.Schema(data_schema),errors=errors)

	async def async_step_import(self, import_data: dict):
		return await self.async_step_user(import_data)
