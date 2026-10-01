# Instruções para agentes de código

## Estrutura atual

- `src/collectors/simulator.py`: gera leituras simuladas.
- `src/models/sensor_reading.py`: modelo e serialização JSON de uma leitura.
- `src/producers/sensor_producer.py`: publica leituras no Kafka.
- `src/consumers/sensor_consumer.py`: consome leituras do Kafka e imprime os campos no terminal.
- `src/kafka_config.py`: fornece configuração compartilhada de `KAFKA_BOOTSTRAP_SERVERS`.
- `src/ingestion.py`: experimento independente que consulta a API do Array of Things; não integra o pipeline Kafka atual.
- `src/api/`, `src/dashboard/` e `src/detectors/`: diretórios com apenas `__init__.py`; não representam funcionalidades implementadas.
- `docker/`: Dockerfile e Compose para ambiente de desenvolvimento, Kafka e ZooKeeper.
- `requirements.txt`: dependências Python.
- `docs/`: estado, arquitetura e decisões do projeto.
- `tests/unit/`: testes pytest para modelo, simulador e configuração/clientes Kafka mockados.
- `tests/integration/`: round trip opcional producer/Kafka/consumer, dependente de broker.

## Comandos relevantes

Na raiz do repositório:

- Instalar dependências: `python -m pip install -r requirements.txt`.
- Subir ambiente: `docker compose -f docker/docker-compose.yml up --build`.
- Encerrar ambiente: `docker compose -f docker/docker-compose.yml down`.
- Executar producer no container de desenvolvimento: `docker compose -f docker/docker-compose.yml exec dev-env python -m src.producers.sensor_producer`.
- Executar consumer no container de desenvolvimento: `docker compose -f docker/docker-compose.yml exec dev-env python -m src.consumers.sensor_consumer`.
- Executar testes unitários: `python -m pytest -m "not integration"`.
- Executar teste de integração: iniciar Compose e executar `docker compose -f docker/docker-compose.yml exec dev-env sh -c 'RUN_KAFKA_INTEGRATION=1 python -m pytest -m integration'`.

Os dois processos Kafka acima são executados separadamente. O comando padrão do container inicia Jupyter Lab.
O padrão do broker é `kafka:29092`; para execução no host, defina `KAFKA_BOOTSTRAP_SERVERS=localhost:9092`.

## Regras de trabalho e segurança

- Não alterar infraestrutura, imagens, versões, listeners, portas, volumes ou topologia Docker sem confirmação do usuário.
- Não descartar arquivos ou dependências sem apresentar a justificativa e obter a decisão aplicável.
- Não incluir segredos, tokens ou credenciais em código, documentação ou commits. Use configuração externa apropriada para valores sensíveis.
- Não fazer commit ou push sem solicitação explícita.
- Antes de considerar uma alteração concluída, executar os testes relevantes e relatar o resultado. Se não houver testes para a área alterada, declarar essa limitação e propor a cobertura necessária.
- Atualizar a documentação quando uma mudança alterar a arquitetura ou o comportamento operacional.
- Preservar o fluxo implementado e distinguir claramente fatos atuais de planos futuros.
