# HR Portal — Запуск приложения

## Структура проекта

```
lab_04.1/
├── src/
│   ├── backend/
│   │   ├── main.py          # FastAPI приложение
│   │   ├── seed.py          # Генерация 10 000 сотрудников
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/
│       ├── app.py           # Streamlit интерфейс
│       ├── requirements.txt
│       └── Dockerfile
├── k8s/
│   └── fullstack.yaml       # Манифесты Kubernetes
└── startup.md
```

---

## Шаг 1 — Сборка Docker-образов

Выполните из корня `lab_04.1/`:

```bash
docker build -t hr-backend:v1 ./src/backend
docker build -t hr-frontend:v1 ./src/frontend
```

---

## Шаг 2 — Импорт образов в MicroK8s

MicroK8s использует собственный runtime, поэтому образы нужно импортировать:

```bash
docker save hr-backend:v1 | microk8s ctr image import -
docker save hr-frontend:v1 | microk8s ctr image import -
```

Убедитесь, что образы появились:

```bash
microk8s ctr images ls | grep hr-
```

---

## Шаг 3 — Развёртывание в Kubernetes

```bash
microk8s kubectl apply -f k8s/fullstack.yaml
```

Проверьте статус подов (подождите ~30–60 секунд):

```bash
microk8s kubectl get pods
```

Все поды должны быть в статусе `Running`:

```
NAME                               READY   STATUS    RESTARTS
postgres-deploy-xxx                1/1     Running   0
backend-deploy-xxx                 1/1     Running   0
frontend-deploy-xxx                1/1     Running   0
```

---

## Шаг 4 — Заполнение базы данных (10 000 строк)

Дождитесь, пока бэкенд-под перейдёт в `Running`, затем выполните seed-скрипт прямо в поде:

```bash
# Узнайте имя пода бэкенда
BACKEND_POD=$(microk8s kubectl get pods -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Скопируйте seed.py в под
microk8s kubectl cp src/backend/seed.py $BACKEND_POD:/app/seed.py

# Запустите скрипт
microk8s kubectl exec $BACKEND_POD -- python seed.py
```

Вывод должен быть:
```
Seeding 10000 employees...
Done.
```

---

## Шаг 5 — Открыть приложение

Откройте в браузере:

```
http://localhost:30080
```

или если работаете с удалённой ВМ — используйте её IP-адрес:

```
http://<IP_ВИРТУАЛЬНОЙ_МАШИНЫ>:30080
```

---

## Возможные проблемы

### Бэкенд перезапускается (CrashLoopBackOff)
Бэкенд ждёт PostgreSQL 7 секунд при старте. Если PostgreSQL ещё не готов — под перезапустится автоматически. Подождите 1–2 минуты, это нормальное поведение.

```bash
microk8s kubectl logs deployment/backend-deploy
```

### Не удаётся подключиться к http://localhost:30080
Проверьте, что NodePort-сервис активен:

```bash
microk8s kubectl get svc frontend-service
```

Убедитесь, что порт 30080 не заблокирован файрволом на ВМ:

```bash
sudo ufw allow 30080
```

### Образы не найдены (ErrImageNeverPull)
Повторите импорт образов из Шага 2. Проверьте правописание тегов — они должны точно совпадать с `image:` в `fullstack.yaml`.

---

## Пересборка и обновление

Если вносите изменения в код:

```bash
# Пересобрать
docker build -t hr-backend:v1 ./src/backend

# Переимпортировать
docker save hr-backend:v1 | microk8s ctr image import -

# Перезапустить под
microk8s kubectl rollout restart deployment/backend-deploy
```

---

## Удаление

```bash
microk8s kubectl delete -f k8s/fullstack.yaml
```
