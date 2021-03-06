from uuid import uuid4

class Key(object):
    """
        Key stores the deserialized Avro record for the Kafka key.
    """

    # Use __slots__ to explicitly declare all data members.
    __slots__ = ["url", "id"]

    def __init__(self, url=None):
        self.url = url
        # Unique id used to track produce request success/failures.
        # Do *not* include in the serialized object.
        self.id = uuid4()

    def key_to_dict(self, ctx):
        return dict(url=self.url)

    def dict_to_key(d, ctx):
        return Key(d['url'])
        

class Value(object):
    """
        Count stores the deserialized Avro record for the Kafka value.
    """

    # Use __slots__ to explicitly declare all data members.
    __slots__ = ["text", "scraper_dt", "id"]

    def __init__(self, text=None, scraper_dt=None):
        self.text = text
        self.scraper_dt = scraper_dt
        # Unique id used to track produce request success/failures.
        # Do *not* include in the serialized object.
        self.id = uuid4()


    def value_to_dict(self, ctx):
        """
        Returns a dict representation of a Value instance for serialization.
        Args:
            user (User): User instance.
            ctx (SerializationContext): Metadata pertaining to the serialization
                operation.
        Returns:
            dict: Dict populated with value attributes to be serialized.
        """
        return dict(text=self.text, scraper_dt=self.scraper_dt)

    def dict_to_value(d, ctx):
        return Value(text=d['text'], scraper_dt=d['scraper_dt'])

