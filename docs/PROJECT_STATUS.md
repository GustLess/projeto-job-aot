# Estado do projeto

## Fluxo implementado

```text
SensorSimulator
      ↓
SensorProducer
      ↓
Kafka: sensor-readings
      ↓
SensorConsumer
      ↓
impressão no terminal
```

O simulador cria leituras com temperatura, umidade, pressão, identificador e timestamp. O producer serializa cada leitura como JSON e publica no tópico `sensor-readings`. O consumer lê esse tópico, converte o JSON em `SensorReading` e imprime seus campos.

## Estado das funcionalidades

- Simulação de leituras: implementada em `src/collectors/simulator.py`.
- Modelo e serialização de leituras: implementados em `src/models/sensor_reading.py`.
- Publicação Kafka: implementada em `src/producers/sensor_producer.py` usando `kafka-python`. O producer aguarda o resultado do envio e reporta erros Kafka básicos.
- Consumo Kafka e impressão no terminal: implementados em `src/consumers/sensor_consumer.py` usando `kafka-python`. Mensagens com bytes/JSON inválidos ou dados incompatíveis são reportadas e ignoradas; erros Kafka básicos são reportados.
- Endereço do broker: producer e consumer compartilham `KAFKA_BOOTSTRAP_SERVERS`, com padrão `kafka:29092`; o serviço `dev-env` recebe esse padrão via Compose. O host pode definir `localhost:9092`.
- Consulta experimental à API Array of Things: existe em `src/ingestion.py`, mas é independente do pipeline descrito acima.
- Detector de anomalias: **NÃO implementado**. O simulador pode gerar leituras fora das faixas usuais; isso não é um detector.
- Persistência: **NÃO implementada**.
- API do projeto: **NÃO implementada**. `src/ingestion.py` é um cliente experimental de API externa, não uma API servida pelo projeto.
- Dashboard: **NÃO implementado**.
- Testes unitários: implementados em `tests/unit/`, incluindo cobertura do modelo, serialização, validações, simulador e configuração dos clientes com mocks. **Ainda não executados nesta auditoria:** o ambiente não tem pytest nem kafka-python instalados.
- Teste de integração Kafka: implementado separadamente em `tests/integration/`, opt-in por `RUN_KAFKA_INTEGRATION=1`. **Não verificado:** o daemon Docker não está acessível neste ambiente.

## Ambiente e pendências

O Compose declara Kafka e ZooKeeper e um container `dev-env` com Jupyter Lab como comando padrão. O serviço Kafka tem healthcheck de disponibilidade do broker e `dev-env` aguarda o serviço ficar saudável. Os clientes usam configuração de ambiente compartilhada; o valor configurado no Compose é `kafka:29092`, e para o host o listener anunciado é `localhost:9092`.

`requirements.txt` contém `kafka-python==2.2.15` e `confluent-kafka`; o pipeline atual importa `kafka-python`. Um script isolado em `.ipynb_checkpoints/teste_kafka-checkpoint.py` usa `confluent-kafka` e outro tópico, mas não integra o pipeline.

O arquivo `docker/docker-compose.yml` fixa Kafka em `7.5.0`, mas usa `latest` para ZooKeeper, o que torna essa imagem mutável. O Dockerfile usa `python:3.11-slim`, também sem digest de imagem. Essas opções foram registradas, não alteradas. A validação estática `docker compose config --quiet` passou; execução real do broker e do pipeline ponta a ponta não foi possível, portanto o fluxo não está confirmado como funcional ponta a ponta.
