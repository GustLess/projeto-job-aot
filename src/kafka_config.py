"""Configuração compartilhada dos clientes Kafka."""

import os


DEFAULT_KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"


def get_kafka_bootstrap_servers() -> str:
    """Retorna os brokers configurados, usando o endereço interno do Compose."""

    return os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", DEFAULT_KAFKA_BOOTSTRAP_SERVERS
    )
