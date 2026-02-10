from aio_pika import ExchangeType, Message, DeliveryMode
import structlog
from .connection import RabbitConnection
from .models import MessagePayload


class RabbitPublisher:
    def __init__(self, connection: RabbitConnection):
        self._connection = connection
        self.logger = structlog.get_logger(__name__)

    async def publish(
        self,
        exchange: str,
        routing_key: str,
        payload: MessagePayload,
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

            await exchange_obj.publish(message, routing_key=routing_key)
            self.logger.info("published", exchange=exchange, routing_key=routing_key)

        except Exception as e:
            self.logger.error(f"Error publishing message: {e}")
            raise
