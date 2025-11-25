# 🔐 Identity & Orders Microservices — com API Gateway (Python / FastAPI)

> ## Em desenvolvimento

Este projeto demonstra uma **arquitetura moderna de microserviços** em Python, com autenticação e autorização baseadas em **OAuth 2.1 / OpenID Connect**.

O sistema é composto por três serviços independentes:

```bash
📦 services/
├─ identity-svc/ → Serviço de identidade (OAuth / OIDC Provider)
├─ orders-svc/ → Serviço de domínio protegido (Pedidos)
└─ gateway-svc/ → API Gateway (entrada única, segurança e roteamento)
```

---

## 🚀 Visão geral da arquitetura

### 🧩 Componentes

| Serviço | Porta | Responsabilidade principal |
|----------|--------|----------------------------|
| **identity-svc** | `8000` | Provedor OAuth / OpenID Connect. Emite tokens, publica JWKS e endpoints `.well-known`. |
| **orders-svc** | `8001` | Serviço de domínio protegido. Requer um **JWT** válido para acesso. |
| **gateway-svc** | `8080` | Ponto de entrada único. Valida tokens, aplica rate limit, roteia para os serviços internos. |

Fluxo resumido:

> Client → [ gateway-svc ] → [ identity-svc | orders-svc ]

## 🧱 Tecnologias principais

| Categoria | Tecnologias |
|------------|--------------|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Autenticação** | OAuth 2.1 + OpenID Connect (via JWT RS256) |
| **Criptografia** | [python-jose](https://github.com/mpdavis/python-jose) |
| **HTTP Client** | [httpx](https://www.python-httpx.org/) |
| **Containerização** | Docker / Docker Compose |
| **Rate limiting** | Token bucket (in-memory) |
| **Circuit breaker** | Fallback simples com reabertura automática |
| **Observabilidade** | Logs estruturados + Request ID por requisição |
| **CORS** | Middleware configurado no gateway |

## 🗂️ Estrutura de pastas (DDD-lite)

Cada serviço segue um layout inspirado em **Domain-Driven Design**, de forma leve e pragmática:

```bash
1️⃣ identity-svc (8000)
   ├─ Geração de chaves RSA (JWKS)
   ├─ Endpoints OAuth (.well-known, /token, /authorize)
   ├─ Emissão de JWT
   └─ CRUD simples de usuários

2️⃣ orders-svc (8001)
   ├─ Validação de JWT (verifica assinatura)
   ├─ CRUD de pedidos
   └─ Autorização por scope/claims

3️⃣ gateway-svc (8080)
   ├─ Roteamento para serviços
   ├─ Validação de tokens
   ├─ Rate limiting
   └─ Circuit breaker
```