# nginx с зашитой конфигурацией.
# Образ собирается вместо bind-mount ./nginx/nginx.conf: в DinD (GitLab CI)
# daemon не видит файловую систему job-контейнера, поэтому конфигурация
# передаётся через build context. Локально поведение идентично.
FROM nginx:1.29-alpine@sha256:5616878291a2eed594aee8db4dade5878cf7edcb475e59193904b198d9b830de

COPY nginx.conf /etc/nginx/conf.d/default.conf
