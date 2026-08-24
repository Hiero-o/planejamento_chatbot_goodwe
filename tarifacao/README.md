# Modulo de tarifacao do GurAI

Modulo independente para calcular o custo estimado de uma sessao de recarga. O restante do chatbot pode integra-lo importando `PricingCalculator` e `EstablishmentRepository`.

## Como usar

```python
from datetime import datetime
from tarifacao import PricingCalculator

resultado = PricingCalculator().simulate(
    establishment_id="estabelecimento_01",
    charger_id="charger_01",
    start=datetime(2026, 8, 23, 18, 0),
    duration_minutes=40,
    power_kw=7.2,
    bandeira="verde",
)

print(resultado.as_dict())
```

## Registrar e consultar uma sessao

```python
from tarifacao import SessionRepository

sessoes = SessionRepository()
sessoes.save(resultado)

contexto = sessoes.summary_for_gurai(
    estabelecimento_id="estabelecimento_01",
    usuario_id="usuario_01",
    veiculo_id="carro_01",
)
```

`contexto` e um texto resumido para ser adicionado ao contexto enviado ao GurAI. A consulta e filtrada por estabelecimento, usuario e, opcionalmente, veiculo; portanto, o historico de um local nao aparece para outro local.

O arquivo `sessoes.json` usa esta estrutura:

```text
estabelecimentos -> estabelecimento_id -> usuarios -> usuario_id
                 -> veiculos -> veiculo_id -> sessoes[]
```

Para criar dados ficticios de teste:

```python
sessoes.generate_demo_sessions(
    PricingCalculator(),
    "estabelecimento_01",
    [("usuario_01", "carro_01"), ("usuario_02", "carro_02")],
    count=20,
    seed=42,
)
```

Use `seed` quando precisar reproduzir o mesmo cenario. Essas sessoes sao demonstrativas e nao representam medicao real.

A energia estimada e `potencia_kw * duracao_minutos / 60`. Se `energia_kwh` for informada em `ChargingSession`, ela tem prioridade.

## Formula

1. `energia_kwh * tarifa_kwh` gera o custo-base.
2. O periodo aplica o adicional percentual configurado.
3. A bandeira soma um valor por kWh.
4. Impostos configurados incidem sobre o subtotal.
5. A margem do estabelecimento incide depois dos impostos por padrao.

Cada estabelecimento e carregador fica no arquivo `estabelecimentos.json`. Para incluir um novo local, adicione um objeto ao array ou use `EstablishmentRepository.add_establishment()`.

## Regras e limites

- As bandeiras seguem as categorias ANEEL: verde, amarela, vermelha patamar 1 e vermelha patamar 2. Os valores configurados sao `0`, `R$ 0,01885`, `R$ 0,04463` e `R$ 0,07877` por kWh, respectivamente, conforme a pagina consultada da ANEEL.
- A bandeira e definida mensalmente pela ANEEL e nao e um adicional decidido pelo consumo individual. Em um produto real, ela deve ser atualizada por competencia, com data e fonte.
- `17:00-20:00` e uma politica de referencia do prototipo, com adicional de 25%. Horarios de ponta reais dependem da modalidade tarifaria, distribuidora, grupo e contrato. A Enel publica tarifas de aplicacao e modalidades, portanto os periodos devem ser confirmados para cada estabelecimento.
- ICMS, PIS e COFINS estao em zero no exemplo. Eles nao devem ser preenchidos com uma aliquota universal: dependem do regime, localidade, tipo de consumidor, enquadramento e forma de emissao. O catalogo deixa as aliquotas configuraveis.
- A autenticacao em `auth.py` e apenas uma base local para desenvolvimento. Antes de producao, usar um provedor de identidade ou o Firebase, com politica de recuperacao, bloqueio e controle de acesso.

Fontes consultadas:

- ANEEL: https://www.gov.br/aneel/pt-br/assuntos/tarifas/bandeiras-tarifarias
- Enel Sao Paulo: https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-de-energia-eletrica.html

## Testes

Na raiz do repositorio:

```bash
python -m unittest tarifacao.test_tarifacao -v
```
