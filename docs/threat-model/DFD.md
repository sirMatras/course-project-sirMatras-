```mermaid
graph TD
    subgraph Client["Клиент (недоверенная зона)"]
        User["Пользователь"]
    end

    subgraph Server["Сервер (доверенная зона)"]
        FastAPI["FastAPI App"]
        UserDB["User DB"]
        WorkoutDB["Workout DB"]
    end

    User -->|F1: HTTPS POST /auth/register<br/>(email, password)| FastAPI
    User -->|F2: HTTPS POST /auth/login<br/>(email, password)| FastAPI
    User -->|F3: HTTPS POST /api/v1/workouts<br/>(JWT, workout data)| FastAPI
    User -->|F4: HTTPS GET /api/v1/workouts/1<br/>(JWT)| FastAPI
    User -->|F5: HTTPS GET /api/v1/stats<br/>(JWT)| FastAPI

    FastAPI -->|F6: SQL INSERT INTO users| UserDB
    FastAPI -->|F7: SQL SELECT FROM users<br/>(WHERE email=?)| UserDB
    FastAPI -->|F8: SQL INSERT INTO workouts| WorkoutDB
    FastAPI -->|F9: SQL SELECT FROM workouts<br/>(WHERE id=? AND user_id=?)| WorkoutDB
    FastAPI -->|F10: SQL SELECT aggregation<br/>(WHERE user_id=?)| WorkoutDB

    classDef clientZone fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef serverZone fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px

    class Client clientZone
    class Server serverZone
```
