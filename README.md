# FraudShield — Transaction Service

Handles payment ingestion for the FraudShield platform. Accepts transaction
requests via REST, persists them to PostgreSQL, and publishes
`TransactionInitiated` events to Kafka. Listens for `FraudVerdict` events and
updates each transaction's status accordingly.

> **Part of the FraudShield microservices system.**
> Companion repo:
> [fraudshield-fraud-detection-service](https://github.com/vivekbhadra/fraudshield-fraud-detection-service)

---

## Tech Stack

- Python 3.12 + FastAPI
- PostgreSQL (SQLAlchemy ORM)
- Apache Kafka (confluent-kafka)
- Redis (via fraud-detection-service)
- Docker / Kubernetes (Minikube)

---

## Repository Structure

```
.
├── app/
│   ├── db/                     # SQLAlchemy session
│   ├── kafka/                  # Kafka producer & consumer
│   ├── models/                 # ORM models
│   ├── routers/                # FastAPI route handlers
│   ├── schemas/                # Pydantic schemas
│   └── services/               # Business logic
├── tests/                      # Unit tests
├── k8s/
│   ├── 00-namespace-configmap.yaml   # Shared: namespace + config
│   ├── 01-secrets.yaml               # Shared: DB/Redis credentials
│   ├── 02-kafka.yaml                 # Shared: Kafka + Zookeeper
│   ├── 03-databases.yaml             # Shared: Postgres + Redis
│   ├── deployment.yaml               # Transaction Service Deployment
│   └── service.yaml                  # Transaction Service (NodePort)
├── scripts/
│   ├── deploy.sh               # Minikube full-stack deploy script
│   ├── test_fraud_block.sh     # End-to-end smoke test
│   └── bootstrap.sh            # Kafka topic bootstrap helper
├── docker-compose.yml          # Full local stack (both services)
├── deploy.sh                   # Minikube deploy script (root copy)
├── FraudShield.postman_collection.json
├── LOCAL_TESTING_GUIDE.md
└── requirements.txt
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/transactions/` | Submit a new transaction |
| GET | `/transactions/{id}` | Get transaction status |
| GET | `/transactions/user/{user_id}` | List transactions for a user |
| GET | `/health` | Health check |

Swagger UI: `http://localhost:18003/docs` (after port-forward)

---

## Quick Start — Docker Compose

Runs both services plus all infrastructure locally:

```bash
docker compose up --build
# Transaction Service → http://localhost:8003/docs
# Fraud Detection     → http://localhost:8004/docs
```

See `LOCAL_TESTING_GUIDE.md` for the full test sequence.

---

## Quick Start — Minikube (Kubernetes)

```bash
minikube start
chmod +x deploy.sh
./deploy.sh
```

The script builds Docker images inside Minikube's daemon, applies all manifests
in dependency order, validates secrets, waits for every pod to be healthy, then
runs a port-forward health check. On success it prints live endpoints.

```bash
# Access services
kubectl port-forward service/transaction-service    18003:8003 -n fraudshield
kubectl port-forward service/fraud-detection-service 18004:8004 -n fraudshield

# Swagger UI
# http://localhost:18003/docs
# http://localhost:18004/docs

# Run the end-to-end smoke test
./scripts/test_fraud_block.sh

# Open Kubernetes dashboard
minikube dashboard
```

---

## Running Tests

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

---

## Docker (standalone)

```bash
docker build -t fraudshield-transaction:1.0.0 .
docker run -p 8003:8003 \
  -e DATABASE_URL=postgresql://fraudshield:fraudshield123@localhost:5432/transactions_db \
  -e KAFKA_BROKER=localhost:9092 \
  fraudshield-transaction:1.0.0
```
