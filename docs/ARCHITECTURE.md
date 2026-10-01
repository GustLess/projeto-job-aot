# Arquitetura atual

## Pipeline Kafka

```text
SensorSimulator
      ↓ cria SensorReading
SensorProducer
      ↓ JSON, tópico sensor-readings
Kafka (listener interno: kafka:29092)
      ↓ grupo anomaly-detector
SensorConsumer
      ↓ valida/decodifica SensorReading
impressão no terminal
```

O producer chama `SensorSimulator.generate_reading()`, serializa o objeto por `to_json()` e envia a mensagem ao Kafka. O consumer lê `sensor-readings`, decodifica UTF-8, constrói uma instância por `SensorReading.from_json()` e imprime sensor, temperatura, umidade e pressão. O grupo configurado no consumer se chama `anomaly-detector`, mas não há detector implementado.

Producer e consumer consultam `KAFKA_BOOTSTRAP_SERVERS` por meio de `src/kafka_config.py`. O padrão é `kafka:29092`, listener interno anunciado pelo Compose. O serviço `dev-env` define esse valor explicitamente. Para execução no host, pode-se definir `KAFKA_BOOTSTRAP_SERVERS=localhost:9092`, listener externo publicado pelo Compose. A política `enable_auto_commit=True` permanece inalterada nesta etapa.

## Infraestrutura de desenvolvimento

`docker/docker-compose.yml` define:

- ZooKeeper na porta interna `2181`;
- Kafka com listener interno em `29092` e externo publicado em `9092`;
- `dev-env`, construído a partir de `docker/Dockerfile`, com o repositório montado em `/app` e portas publicadas para Jupyter (`8888`) e Streamlit (`8501`).

O comando padrão do Dockerfile inicia Jupyter Lab. Kafka tem um healthcheck que consulta o broker e `dev-env` aguarda Kafka ficar saudável por `depends_on: condition: service_healthy`. Kafka e ZooKeeper se comunicam conforme configurado no Compose.

## Código fora do pipeline

`src/ingestion.py` consulta a API externa Array of Things e retorna observações em um DataFrame. Não é chamado pelo producer/consumer atual. `src/api/`, `src/dashboard/` e `src/detectors/` contêm apenas inicializadores vazios nesta revisão.

## Componentes futuros

Detector de anomalias, persistência, API do projeto e dashboard são **FUTUROS / NÃO IMPLEMENTADOS**. Nenhum deles participa do fluxo atual. Testes unitários e um teste de integração opt-in foram adicionados, mas não foram executados neste ambiente: pytest e kafka-python não estão instalados e o daemon Docker não está acessível. O Compose foi validado estaticamente; isso não confirma execução ponta a ponta.
