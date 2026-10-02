# Arquitetura atual

## Pipeline Kafka

```text
SensorSimulator → SensorProducer → Kafka: sensor-readings
    → SensorConsumer → decode/validação → RuleBasedAnomalyDetector
    → NORMAL ou ANOMALY no terminal
```

O producer serializa `SensorReading.to_json()` e aguarda confirmação Kafka.
O consumer usa `process_message()` para decodificar UTF-8, construir/validar o
modelo e classificar. `consume_messages()` reporta e ignora eventos inválidos,
continuando o consumo. Nenhum resultado é persistido ou publicado em outro tópico.

## Contrato de evento v1

| Campo | Contrato |
| --- | --- |
| event_id | Texto não vazio; UUID v4 automático na criação local, preservado no round trip |
| sensor_id | Texto não vazio |
| timestamp | ISO 8601 com UTC explícito (`Z` ou `+00:00`); criação usa UTC atual |
| temperature | Número finito, °C |
| humidity | Número finito, % |
| pressure | Número finito, hPa |
| source | Texto não vazio; padrão local `simulator` |
| schema_version | Inteiro 1; booleanos e outras versões rejeitados |

Os oito campos são obrigatórios no JSON. Campos desconhecidos são rejeitados.
A construção local anterior continua possível graças aos defaults dos novos
campos. Mensagens antigas sem metadados são ignoradas: não se inventa identidade
no consumo. O produtor é responsável pela unicidade; não há deduplicação nem
verificação global de IDs. Identificadores externos não precisam ser UUIDs.

Validação responde se o evento respeita o contrato: não aceita textos numéricos,
booleanos, NaN ou infinitos. Não impõe limites físicos ou limites do detector.
Detecção responde se um evento válido está fora das faixas configuradas.

## Detector de regras v1.0.0

`DEFAULT_RULES` em `src/detectors/anomaly_detector.py` centraliza as faixas
inclusivas. Um valor exatamente no limite é normal. O construtor aceita regras
personalizadas e copia a configuração para uma tupla de regras imutáveis.
`process_message()` aceita um detector injetado; `consume_messages()` cria um
detector por laço quando não recebe um e o reutiliza entre mensagens.

| Variável | Faixa normal | Extremos injetados pelo simulador |
| --- | --- | --- |
| temperature | 20–30 °C | 60–100 °C |
| humidity | 40–75% | 90–100% |
| pressure | 1000–1025 hPa | 850–930 hPa |

Essas faixas reproduzem os intervalos normais sintéticos existentes, garantindo
que todos os extremos deliberados sejam detectáveis. Valores inferiores ou
superiores à faixa disparam `below_minimum` ou `above_maximum`.

`DetectionResult` contém `event_id`, `is_anomaly`, todas as `violations`,
`detector_name`, `detector_version` e `detected_at` UTC. Cada violação registra
variável, valor observado, mínimo, máximo e regra violada. `to_dict()` produz
um objeto serializável com lista de violações; internamente usa tupla imutável.

O detector valida defensivamente a entrada. Não aprende, não usa histórico,
não considera contexto por sensor nem correlação entre variáveis. Os limites
servem aos dados sintéticos e não constituem calibração para sensores reais.

## Configuração e infraestrutura preservadas

Producer e consumer usam `KAFKA_BOOTSTRAP_SERVERS` via `src/kafka_config.py`:
`kafka:29092` no Compose e `localhost:9092` para o host. O consumer mantém
`group_id=anomaly-detector`, `auto_offset_reset=earliest` e `enable_auto_commit=True`.

O Compose mantém ZooKeeper (2181), Kafka (listener interno 29092, externo 9092)
e `dev-env` (Jupyter 8888, porta 8501 publicada). O Dockerfile inicia Jupyter Lab.
O healthcheck Kafka condiciona a inicialização de `dev-env`. Nenhuma imagem,
versão, porta, volume ou topologia foi alterada.

`src/ingestion.py` permanece um experimento independente com a API Array of Things.
API e dashboard do projeto não estão implementados. ML, Data Lake, Parquet,
DuckDB, banco de dados e persistência de resultados não integram este pipeline.
