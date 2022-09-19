class CustomSerializerMixin:
    def update(self, instance, validated_data):
        raise Exception('This serializer called only for GET method request with list action')

    def create(self, validated_data):
        raise Exception('This serializer called only for GET method request with list action')