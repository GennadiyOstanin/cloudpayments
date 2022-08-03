import aiohttp
import base64
from datetime import datetime

from abstract_client import AbstractInteractionClient, InteractionResponseError


class TestClient(AbstractInteractionClient):
    SERVICE = 'cloudpayments'
    BASE_URL = 'https://api.cloudpayments.ru/'

    def __init__(self, public_id: str, api_secret: str):
        super().__init__()
        self.CONNECTOR = aiohttp.TCPConnector(limit=30)

        self.public_id = public_id

        token = f'{public_id}:{api_secret}'.encode('utf-8')
        decoded_token = base64.b64encode(token).decode('utf-8')

        self.headers_template = {
            'Authorization': f'Basic {decoded_token}',
            'Content-Type': 'application/json',
        }

    def _make_request_id(self, ip_address: str) -> str:
        return str(datetime.timestamp(datetime.now())) + ip_address

    def _get_optional_data(self, optional_keys: list, **kwargs):
        data = {}
        for key in optional_keys:
            if key in kwargs:
                data[key] = kwargs[key]
        return data

    async def charge(self, amount: float, ip_address: str, card_cryptogram_packet: str, **kwargs):
        """
        :param amount: float
        :param card_cryptogram_packet: str
        :param ip_address: str
        :param kwargs optional fields
        """

        data = {
            'Amount': amount,
            'IpAddress': ip_address,
            'CardCryptogramPacket': card_cryptogram_packet,
            'PublicId': self.public_id,
        }

        optional_keys = ['invoice_id', 'currency', 'name', 'payment_url', 'description', 'culture_name', 'account_id',
                         'email']
        data.update(self._get_optional_data(optional_keys, **kwargs))

        self.headers_template['X-Request-ID'] = self._make_request_id(ip_address)

        try:
            response = await self.post(
                interaction_method='charge',
                url=self.endpoint_url('payments/charge'),
                headers=self.headers_template,
                data=data,
            )
        except InteractionResponseError as e:
            return 'request failed'  #TODO handle error
        if not response['Success']:
            return 'request failed'  #TODO handle error

        return response
