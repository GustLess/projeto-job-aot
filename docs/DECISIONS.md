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
- O pipeline termina imprimindo a classificação e todas as violações no terminal. Não há armazenamento de resultados.

## Pendências que exigem decisão

- **Confirmação de consumo:** escolher política de commit. O auto commit atual pode avançar offsets antes de um processamento confiável, enquanto o efeito atual é apenas imprimir no terminal. Se o processamento passar a persistir/produzir resultado, avaliar commit manual somente após sucesso do processamento, com tratamento de falhas e reentrega. Não mudar o comportamento nesta etapa.
- **Reprodutibilidade de imagens:** decidir política de pinagem para ZooKeeper (`latest`) e para a imagem Python, sem atualização automática de versões.
- **Validação contínua:** testes unitários e integração Kafka passaram na etapa 2; manter a integração opt-in em ambientes com broker disponível.

## Etapa 2 — contrato e processamento (2026-10-01)

- Modelo dataclass e biblioteca padrão; nenhuma nova dependência no projeto.
- `event_id` automático UUID v4 e `schema_version=1` preservam chamadas locais
  existentes. JSON exige todos os campos, incluindo source e novos metadados:
  eventos legados incompletos são reportados/ignorados, evitando criar identidades
  diferentes para a mesma mensagem a cada consumo. IDs externos não vazios são
  aceitos; deduplicação/global uniqueness não implementadas.
- Timestamp ISO 8601 deve ter offset UTC explícito. Números devem ser finitos;
  textos e booleanos não são convertidos silenciosamente em medidas.
- Validação não usa faixas do detector; extremos finitos podem ser válidos.
- Faixas inclusivas centralizadas em `DEFAULT_RULES`: temperatura [20,30],
  umidade [40,75], pressão [1000,1025]. Correspondem aos intervalos normais do
  simulador e detectam todos os extremos que ele injeta deliberadamente.
- Resultado estruturado com todas as violações, identidade do evento,
  nome/versão do detector e horário UTC da detecção. Não há histórico, aprendizado,
  calibração real, persistência nem tópico adicional.
- Consumer mantém auto commit e configuração Kafka. Processamento exposto como
  função pura quanto a efeitos externos; laço imprime e ignora mensagens inválidas.
