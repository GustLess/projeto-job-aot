# Decisões e pontos pendentes

## Confirmado pelo estado atual

- O tópico do pipeline é `sensor-readings`.
- Producer e consumer do pipeline usam `kafka-python` (`kafka-python==2.2.15` em `requirements.txt`). O código principal não foi migrado para `confluent-kafka`; essa dependência permanece porque há um experimento antigo que pode usá-la.
- Producer e consumer compartilham a variável `KAFKA_BOOTSTRAP_SERVERS`, com padrão `kafka:29092`, o listener interno anunciado pelo Compose. O host pode usar `localhost:9092` via variável.
- Kafka está configurado com listener externo em `localhost:9092` e porta publicada `9092`.
- O consumer usa o grupo `anomaly-detector`, `auto_offset_reset="earliest"` e `enable_auto_commit=True`.
- O producer espera o resultado do envio Kafka antes de imprimir a confirmação de publicação.
- Compose verifica disponibilidade Kafka por healthcheck e aguarda o broker ficar saudável antes de iniciar `dev-env`.
- Testes unitários foram criados e o teste de integração Kafka está isolado e exige `RUN_KAFKA_INTEGRATION=1`.
- Kafka está fixado em `confluentinc/cp-kafka:7.5.0`; ZooKeeper usa `confluentinc/cp-zookeeper:latest`.
- O pipeline termina imprimindo a leitura no terminal. Não há confirmação de processamento posterior ou armazenamento.

## Pendências que exigem decisão

- **Confirmação de consumo:** escolher política de commit. O auto commit atual pode avançar offsets antes de um processamento confiável, enquanto o efeito atual é apenas imprimir no terminal. Se o processamento passar a persistir/produzir resultado, avaliar commit manual somente após sucesso do processamento, com tratamento de falhas e reentrega. Não mudar o comportamento nesta etapa.
- **Reprodutibilidade de imagens:** decidir política de pinagem para ZooKeeper (`latest`) e para a imagem Python, sem atualização automática de versões.
- **Validação da infraestrutura:** executar testes unitários e de integração em ambiente com pytest, kafka-python e Docker disponíveis. O Compose validou estaticamente, mas Kafka e fluxo ponta a ponta ainda não foram verificados.
