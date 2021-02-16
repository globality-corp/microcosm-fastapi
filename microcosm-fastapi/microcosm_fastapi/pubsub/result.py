from microcosm_pubsub.result import MessageHandlingResult

@dataclass
class MessageHandlingResultAsync(MessageHandlingResult):
    @classmethod
    async def invoke(cls, handler, message: SQSMessage):
        try:
            success = await handler(message.content)
            return cls.from_result(message, bool(success))
        except Exception as error:
            return cls.from_error(message, error)
