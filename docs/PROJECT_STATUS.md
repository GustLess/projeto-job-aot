# Estado do projeto

## Etapa 2 implementada

Fluxo atual: simulador → producer → Kafka `sensor-readings` → consumer →
validação → detector baseado em regras → classificação no terminal.

- Contrato v1 com oito campos, UUID por evento e horário UTC explícito.
- Validação estrutural e de tipos separada da classificação de valores extremos.
- Detector com faixas inclusivas para temperatura, umidade e pressão,
  preservando todas as violações de uma leitura.
- Consumer imprime `NORMAL` ou `ANOMALY`, metadados e regras disparadas.
  Mensagens inválidas são reportadas e ignoradas sem interromper o laço.
- Producer, simulador, configuração Kafka e infraestrutura preservados.
- API, dashboard, ML, Data Lake e persistência não implementados.
- `src/ingestion.py` continua um experimento externo ao pipeline.

Contrato, limites, justificativa e limitações estão em `ARCHITECTURE.md`.
As decisões de compatibilidade estão em `DECISIONS.md`.

## Verificação em 2026-10-01

Os 14 testes unitários iniciais passaram no `dev-env` antes das alterações.
Após a implementação, 64 testes unitários passaram (0 falhas; 2 testes de
integração desmarcados nesse comando). A integração é opt-in com marcador
`integration` e `RUN_KAFKA_INTEGRATION=1`; cobre evento normal e anômalo,
com preservação do round trip e classificação pelo processamento do consumer.

O Python do host não tinha pip/pytest e seu módulo venv não tinha ensurepip.
Os testes principais usam Python 3.11 do container existente. O primeiro
`up --build -d` falhou internamente no Bake; repetir com `COMPOSE_BAKE=false`
permitiu iniciar os serviços, sem alterar arquivos Docker.

Os dois cenários Kafka passaram (2 PASS, 0 FAIL, 0 SKIPPED), com 64 testes
unitários desmarcados no comando de integração. Total executado após as alterações:
66 PASS, 0 FAIL, 0 SKIPPED. `git diff --check` e a validação estática do Compose
passaram. Os serviços iniciados para a validação foram encerrados com `down`.

## Pendências

Limites específicos para sensores reais precisam de calibração. Auto commit
permanece habilitado; avaliar garantias de processamento antes de introduzir
efeitos persistentes. ZooKeeper continua usando imagem `latest`, e Python
`3.11-slim` não tem digest fixado no Dockerfile. Essas decisões de infraestrutura
não foram alteradas nesta etapa.
