from rest_framework import serializers


class IntrospectTokenSerializer(serializers.Serializer):
    token = serializers.CharField(
        max_length=64,
        write_only=True,
    )
    scope = serializers.CharField(
        max_length=256,
        read_only=True,
    )
    exp = serializers.IntegerField(
        read_only=True,
    )
    user = serializers.DictField(
        read_only=True,
    )

    # mutex = serializers.CharField(
    #     max_length=4,
    #     read_only=True,
    # )

    def create(self, validated_data):
        return {k: v for k, v in validated_data.items()}

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')
