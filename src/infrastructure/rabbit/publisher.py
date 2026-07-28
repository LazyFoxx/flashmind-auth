from aio_pika import ExchangeType, Message, DeliveryMode
import structlog
from .connection import RabbitConnection
from src.application.interfaces import AbstractEventPublisher, UserPayload

 
class RabbitPublisher(AbstractEventPublisher):
    def __init__(self, connection: RabbitConnection):
        self._connection = connection
        self.logger = structlog.get_logger(__name__)
        self.exchange = "events"
        self.routing_key = "user.registered"

    async def publish(
        self,
        payload: UserPayload,
    ) -> None:
        try:
            # Сериализуем данные через Pydantic модель
            payload_json = (
                payload.json()
            )  # Pydantic автоматически валидирует и сериализует

            channel = self._connection.channel
            # Объявляем exchange (idempotent, безопасно повторно)
            exchange_obj = await channel.declare_exchange(
                name="events",
                type=ExchangeType.DIRECT,
                durable=True,
                auto_delete=False,
            )

            message = Message(
                body=payload_json.encode(),  # Кодируем данные в байты
                delivery_mode=DeliveryMode.PERSISTENT,  # Сообщения сохраняются на диск
            )

            await exchange_obj.publish(message, routing_key=self.routing_key)
            self.logger.info("published", exchange=self.exchange, routing_key=self.routing_key)

        except Exception as e:
            self.logger.error(f"Error publishing message: {e}")
            raise
