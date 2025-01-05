# Поисковый сервис. 

## Описание.
Сервис предназначен для поиска информации по фильмам онлайн кинотеатра.

### Архитектурное решение:
- **серверная часть**: сервер на FastAPI для обработки запросов пользователей по фильмам, жанрам и персонам;
- **поисковый движок**: ElasticSearch для поиска информации по фильмам;
- **etl**: python приложение для переноса данных по фильмам из базы данных PostgreSQL в ElasticSearch;
- **хранилище кешированных запросов**: Redis для кеширования запросов пользователей c ограниченным временем хранения данных;
- **эндпоинты /films/...**: для просмотра информации по фильму / фильмам, полнотекстового поиска по фильмам;
- **эндпоинты /genres/...**: для просмотра информации по жанру / жанрам;
- **эндпоинты /persons/...**: для просмотра информации по персоне / персонам, полнотекстового поиска по персонам;
- **документация OpenAPI**: встроенная автоматически генерируемая документация FastAPI на основе спецификаций OpenAPI.

### Тесты.
Сделаны тесты для проверки работоспособности всех эндпоинтов сервиса.

### Основные команды для запуска сервиса:
- **запуск сервиса в docker compose**: 
`docker compose up -d`;
- **остановка сервиса**: 
`docker compose down`;
- **запуск тестов**: 
`docker compose -f src/tests/functional/docker-compose.yml up -d`;
- **завершение тестов**: 
`docker compose -f src/tests/functional/docker-compose.yml down -v`.

Более подробно все основные команды представлены в [Makefile](Makefile).
