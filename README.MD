# trivelta-lab

Laboratorio de estudio: una plataforma B2B mínima de sportsbook multi-operador,
construida con el stack de Trivelta / NextGen Ventures.

**No es un producto.** Es un banco de pruebas para dominar el stack y demostrar que los
patrones difíciles —concurrencia sobre dinero, idempotencia, aislamiento multi-tenant—
se trasladan de Ruby on Rails a Python sin perder el criterio.

---

## Por qué este dominio

Una plataforma de apuestas y un facturador fiscal comparten los problemas difíciles.
Cambian los nombres, no la sustancia:

| Problema real | En facturación (Rails) | Aquí (Python) |
|---|---|---|
| Aislar clientes en una sola app | multitenancy por `tenant_id` | multi-operador por `operator_id` |
| Un saldo que nunca puede quedar mal | `CreditWallet` con lock pesimista | `Wallet` con `SELECT … FOR UPDATE` |
| Nunca cobrar/pagar dos veces | compare-and-swap sobre el estado | header `Idempotency-Key` |
| Trabajo lento fuera del request | Sidekiq + Redis | Celery + Redis |
| Demostrarle algo a un regulador | CFDI 4.0 y el SAT | AML / KYC |
| Abuso automatizado | Rack::Attack | rate limiting + reglas de fraude |

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | **Python 3.12** · FastAPI · Pydantic |
| ORM / DB | **SQLAlchemy 2** · Alembic · **PostgreSQL 17** |
| Cola | **Celery** · Redis |
| Frontend | **Next.js 15** · React · **TypeScript** · TanStack Query |
| Testing | **pytest** · httpx |
| CI | **GitHub Actions** |
| Contenedores | **Docker** · docker-compose |
| Runtimes | **mise** (`.mise.toml` fija Python 3.12 y Node 22) |

---

## Estructura — monorepo

```
trivelta-lab/
├── .mise.toml              # versiones de runtime del proyecto
├── .github/workflows/      # CI: tests, linter, build
├── backend/
│   ├── .venv/              # entorno virtual (NO se commitea)
│   ├── requirements.txt
│   ├── alembic/            # migraciones
│   ├── app/
│   │   ├── main.py         # arranque de FastAPI
│   │   ├── db.py           # engine y sesión
│   │   ├── models.py       # tablas SQLAlchemy
│   │   └── routers/        # endpoints por recurso
│   └── tests/
└── frontend/               # Next.js + TS
```

**Monorepo, no polyrepo.** Backend y frontend cambian juntos, un solo pipeline de CI
prueba ambos, y se demuestra abriendo un solo repositorio. Polyrepo tiene sentido con
equipos separados y ciclos de release independientes — no es el caso.

---

## Modelo de dominio

```
Operator  (el tenant: cada casa de apuestas cliente)
   └── Player          (jugador de ese operador)
         └── Wallet    (saldo — una por jugador)
               └── Transaction   (ledger inmutable: depósito, apuesta, premio)
Event      (partido con sus cuotas)
   └── Bet             (apuesta de un jugador sobre un evento)
         └── Settlement (liquidación: ganó o perdió)
```

**Regla de oro:** el saldo **nunca** se edita directamente. Siempre se crea una
`Transaction` y el saldo se deriva de ella. Misma regla que el ledger de créditos en
facturación — así el historial es auditable y un regulador puede reconstruirlo.

---

## Roadmap por rebanadas

Rebanadas **verticales**: cada una funciona de punta a punta antes de pasar a la
siguiente. Nada de "primero todo el backend".

### Fase 1 — antes del panel técnico (~7.5 h)

- [ ] **0. Setup** — mise, venv, FastAPI, SQLAlchemy, Alembic, pytest, `/health`
- [ ] **1. CI en GitHub Actions** — desde el primer commit: pytest + linter en verde
- [ ] **2. Wallet con lock pesimista** — `debit()` en transacción, con test de concurrencia
      que pruebe que dos débitos simultáneos no dejan saldo negativo
- [ ] **3. `POST /bets` idempotente** — header `Idempotency-Key`; reenviar la misma
      petición devuelve el mismo resultado sin cobrar dos veces
- [ ] **4. Frontend mínimo** — Next.js + TS + TanStack Query: ver saldo y colocar apuesta

### Fase 2 — después del panel

- [ ] **5. Multi-operador** — JWT + scoping por `operator_id` en cada query, con tests
      que prueben que un operador no ve datos de otro
- [ ] **6. Liquidación asíncrona** — Celery + Redis; pagar premios sin bloquear el request,
      con reintentos e idempotencia (at-least-once delivery)
- [ ] **7. KYC** — estados de verificación; retiros bloqueados sin KYC aprobado
- [ ] **8. Detección de fraude** — rate limiting y reglas de alerta (ráfagas de apuestas,
      montos estructurados)
- [ ] **9. Reporteo regulatorio** — export de transacciones por periodo (AML)
- [ ] **10. Observabilidad** — logs estructurados, `/health`, métricas, runbook de incidentes
- [ ] **11. Docker** — `docker-compose` con app, Postgres y Redis; CI corriendo en contenedor

---

## Cómo correr

**Requisitos:** mise, PostgreSQL 17 y Redis corriendo (`brew services list`).

```bash
cd trivelta-lab                     # mise activa Python 3.12 y Node 22

cd backend
source .venv/bin/activate           # el prompt debe mostrar (.venv)
pip install -r requirements.txt
alembic upgrade head                # aplicar migraciones
uvicorn app.main:app --reload       # http://localhost:8000/docs

pytest                              # suite de tests
```

```bash
cd frontend
npm install
npm run dev                         # http://localhost:3000
```

---

## Decisiones técnicas

Se documentan aquí conforme se toman, con una línea de justificación.

| Decisión | Por qué |
|---|---|
| Monorepo | Un solo dev, un solo CI, se demuestra abriendo un repo |
| `venv` + `requirements.txt` | Universalmente reconocible; `uv` es más rápido pero añade una herramienta que explicar |
| Postgres local, no Docker | Ya está corriendo por Homebrew; Docker entra en la rebanada 11 |
| Lock pesimista en el saldo | Es dinero: la colisión es probable y el error es caro. Optimista para lo demás |
| Ledger inmutable | El saldo se deriva de transacciones, nunca se edita — auditable por diseño |
| CI desde el primer commit | Un pipeline agregado al final nunca se agrega |

---

## Equivalencias Ruby → Python

Chuleta para no perderse al cambiar de stack:

| Ruby / Rails | Python |
|---|---|
| `Gemfile` / Bundler | `requirements.txt` / pip + venv |
| `bundle install` | `pip install -r requirements.txt` |
| Rails | FastAPI (minimalista) o Django (todo incluido) |
| ActiveRecord | SQLAlchemy |
| `rails db:migrate` | `alembic upgrade head` |
| `rails db:rollback` | `alembic downgrade -1` |
| RSpec | pytest |
| Sidekiq | Celery |
| `rails server` | `uvicorn app.main:app --reload` |
| `rails console` | `python -i` o IPython |
| `nil` | `None` |
| Bloques | funciones lambda / decoradores |
| Módulos (mixins) | herencia múltiple / composición |

---

## Qué evalúa el panel técnico

Requisitos textuales de su vacante, mapeados a la rebanada que los demuestra:

| Requisito de la vacante | Rebanada que lo cubre |
|---|---|
| Python para backend, automatización y procesamiento de datos | 0, 2, 3 |
| APIs escalables para web, móvil e integraciones de terceros | 3 |
| React, TypeScript, Next.js, TanStack | 4 |
| **CI/CD y automatización de infraestructura** | 1, 11 |
| Pipelines de datos: analítica, **detección de fraude**, reporteo regulatorio | 8, 9 |
| Compliance: **AML, KYC**, privacidad de datos | 7, 9 |
| Respuesta a incidentes y monitoreo | 10 |
| Mentoría y decisiones de arquitectura | este README |

Es un puesto **senior**: esperan criterio y decisiones justificadas, no volumen de código.
Por eso la sección de *Decisiones técnicas* de arriba importa tanto como el código.

---

## Glosario — el vocabulario que hay que dominar

Conceptos destilados de la sesión de estudio. Este proyecto existe para **demostrar
cada uno con código**, no para recitarlos.

### Concurrencia y consistencia

| Término | Qué significa | Dónde se demuestra |
|---|---|---|
| **Bloqueo pesimista** | Bloqueo la fila antes de tocarla; los demás esperan. Para dinero, donde la colisión es probable y el error es caro | Rebanada 2 |
| **Bloqueo optimista** | No bloqueo; al guardar verifico que nadie más cambió. Para colisiones raras | Rebanada 6 |
| **Compare-and-swap (CAS)** | `UPDATE … WHERE estado = <esperado>`; si afecta 1 fila gané el claim, si afecta 0 alguien se me adelantó | Rebanada 6 |
| **Idempotencia** | Ejecutar dos veces produce el mismo resultado que una vez | Rebanada 3 |
| **At-least-once delivery** | La cola puede entregar el mismo job dos veces. **No es un bug: es el diseño.** El bug sería que el job no fuera idempotente | Rebanada 6 |
| **Transacción / ACID** | Atomicidad, Consistencia, Aislamiento, Durabilidad. Todo o nada | Rebanada 2 |
| **Ledger inmutable** | El saldo se deriva de transacciones; nunca se edita. Auditable por diseño | Rebanada 2 |

### Rendimiento

| Término | Qué significa |
|---|---|
| **N+1** | 1 consulta para traer N registros + 1 por cada uno para su relación. Con 100 filas son 101 viajes. Se arregla con *eager loading* |
| **Índice** | Acelera lecturas. **No** lo pongas en tablas chicas, columnas con pocos valores distintos, o tablas con escritura muy frecuente — cada índice hace más lento cada `INSERT` |
| **p50 / p95 / p99** | Percentiles de latencia. El promedio miente con los extremos; **el p99 es el que le duele al cliente** |

### Web y seguridad

| Término | Qué significa |
|---|---|
| **2xx / 3xx / 4xx / 5xx** | Salió bien / redirección / se equivocó el cliente / **se equivocó el servidor (tu bug)** |
| **GET vs POST** | GET mira y no cambia nada; POST actúa. Al auditar logs, los GET son ruido y los POST son la señal |
| **429 + `Retry-After`** | "Demasiadas peticiones". No es una alerta, es un **recibo**: algo tuyo frenó a alguien. El header comunica el límite en vez de solo bloquear |
| **Rate limiting: ventana fija** | El contador se reinicia de golpe → **efecto de frontera**: 2× el límite si el atacante se sincroniza con el borde |
| **La clave del contador** | Contar por IP protege al servidor; contar por recurso protege al recurso. Elegir mal la clave anula la defensa |
| **Fail-open vs fail-closed** | Si el almacén de contadores se cae, ¿dejas pasar todo o bloqueas todo? Disponibilidad contra protección — hay que decidirlo a propósito |
| **Autenticación vs autorización** | Quién eres (JWT) vs qué puedes hacer (políticas). Se puede estar autenticado y no autorizado |
| **Multitenancy** | Una app, muchos clientes, datos aislados. El scope automático **no basta** — hay que probarlo con tests |

### Procesos

| Término | Qué es |
|---|---|
| **Job** | La tarea: una clase que describe qué hacer |
| **Thread** | El ejecutor: un hilo que hace una cosa a la vez |
| **Worker** | El proceso que contiene los threads |

> El job es el *qué*, el thread es el *quién lo hace*, el worker es el *dónde vive*.

---

## Preguntas de entrevista que este proyecto responde

Este dominio garantiza estas preguntas. Cada una tiene su respuesta **en código**:

1. **"¿Cómo evitas que una apuesta se pague dos veces?"**
   → Rebanada 3: `Idempotency-Key`. Rebanada 6: compare-and-swap sobre el estado del
   settlement + lock pesimista sobre el saldo. Defensa en profundidad.

2. **"Mil usuarios apuestan contra el mismo saldo al mismo tiempo. ¿Qué haces?"**
   → Rebanada 2: lock pesimista dentro de una transacción. El trade-off es explícito:
   serializas y pierdes throughput, pero el dinero nunca queda mal.

3. **"¿Cómo aíslas los datos entre operadores en una plataforma B2B?"**
   → Rebanada 5: scoping por `operator_id` **más tests** que prueben la fuga.

4. **"¿Cómo detectas actividad fraudulenta o automatizada?"**
   → Rebanada 8. Y el límite honesto: un atacante lento evade cualquier regla basada en
   ritmo, así que hace falta detectar **patrón**, no solo velocidad.

5. **"Un regulador pide el historial de una cuenta. ¿Lo tienes?"**
   → Rebanada 9, sobre el ledger inmutable de la rebanada 2.

6. **"Tu job se ejecutó dos veces. ¿Es un bug?"**
   → No: es *at-least-once delivery*. El bug sería que no fuera idempotente.

---

## Contexto

Preparación para el panel técnico de **NextGen Ventures / Trivelta** — plataforma B2B
modular de sportsbook y casino, oficinas en Boston, Barcelona, Monterrey e Indore.
Panel técnico: **martes 2026-08-18, 10:00**.

Documentos hermanos, en el repo `facturas`:

| Archivo | Qué contiene |
|---|---|
| `laboratorios/plan_aprendizaje.md` | Plan por módulos con misiones de terminal, preguntas de entrevista, calendario e inteligencia sobre la empresa |
| `laboratorios/estudio.md` | Preguntas y respuestas de la sesión de análisis de logs, rate limiting, Sidekiq y concurrencia — incluida la tabla de errores cometidos |
| `laboratorios/fix_scanner_traffic/` | Lab de análisis de tráfico malicioso real en producción |

**La regla para el martes:** no sabes todo y no tienes que saberlo. Lo que se evalúa es
cómo piensas cuando no sabes. Reconocer un límite y explicar cómo lo resolverías vale
más que una respuesta inventada — y es lo único que no se puede fingir.
