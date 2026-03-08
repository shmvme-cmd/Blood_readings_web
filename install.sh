#!/bin/bash
#---------------------------------------------------------------------
# Install script for МедДневник on Debian/Ubuntu
# https://github.com/shmvme-cmd/med-dnevnik
#---------------------------------------------------------------------

set -e

REPO="https://github.com/shmvme-cmd/med-dnevnik"
ARCHIVE_URL="${REPO}/archive/refs/heads/main.tar.gz"
ARCHIVE_NAME="med-dnevnik-main"
PROJECT_DIR="/usr/bin/med-dnevnik"
SERVICE_NAME="med-dnevnik"
SERVICE_USER="root"
PORT=5001

# ── Root check ────────────────────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    echo "Этот скрипт должен запускаться от root (sudo bash install.sh)"
    exit 1
fi

# ── 1. Системные зависимости ──────────────────────────────────
echo ">>> [1/7] Установка системных зависимостей..."
apt-get update -qq
apt-get install -y --no-install-recommends curl wget ca-certificates

# ── 2. Установка uv ──────────────────────────────────────────
echo ">>> [2/7] Установка uv..."
if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' /root/.bashrc 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.bashrc
    fi
else
    echo "uv уже установлен: $(uv --version)"
fi

UV_BIN="$(command -v uv 2>/dev/null || echo "$HOME/.local/bin/uv")"

if ! "$UV_BIN" --version &>/dev/null; then
    echo "Ошибка: uv не найден после установки."
    exit 1
fi
echo "uv: $("$UV_BIN" --version)"

# ── 3. Загрузка проекта ───────────────────────────────────────
echo ">>> [3/7] Загрузка проекта..."
cd /tmp
rm -rf "${ARCHIVE_NAME}" med-dnevnik.tar.gz
wget -q "${ARCHIVE_URL}" -O med-dnevnik.tar.gz
tar xfz med-dnevnik.tar.gz

# ── 4. Копирование файлов ─────────────────────────────────────
echo ">>> [4/7] Установка файлов в ${PROJECT_DIR}..."
rm -rf "${PROJECT_DIR}"
mkdir -p "${PROJECT_DIR}"
cp -r "/tmp/${ARCHIVE_NAME}/." "${PROJECT_DIR}/"

# ── 5. Создание venv и установка зависимостей ─────────────────
echo ">>> [5/7] Установка зависимостей Python..."
cd "${PROJECT_DIR}"
"$UV_BIN" venv
"$UV_BIN" pip install -e .

# Создать директорию для БД и .env с секретным ключом
mkdir -p "${PROJECT_DIR}/instance"
if [ ! -f "${PROJECT_DIR}/.env" ]; then
    echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > "${PROJECT_DIR}/.env"
    echo "Сгенерирован SECRET_KEY в ${PROJECT_DIR}/.env"
fi

# ── 6. Загрузка статических ресурсов (офлайн-режим) ──────────
echo ">>> [6/7] Загрузка статических ресурсов..."
STATIC_DIR="${PROJECT_DIR}/static"
mkdir -p "${STATIC_DIR}/css/fonts"
mkdir -p "${STATIC_DIR}/js"

# Bootstrap 5.3.3
wget -q "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" \
    -O "${STATIC_DIR}/css/bootstrap.min.css"
wget -q "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" \
    -O "${STATIC_DIR}/js/bootstrap.bundle.min.js"

# Bootstrap Icons 1.11.3
wget -q "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" \
    -O "${STATIC_DIR}/css/bootstrap-icons.min.css"
wget -q "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff2" \
    -O "${STATIC_DIR}/css/fonts/bootstrap-icons.woff2"
wget -q "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff" \
    -O "${STATIC_DIR}/css/fonts/bootstrap-icons.woff"

# Chart.js 4.4.4
wget -q "https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js" \
    -O "${STATIC_DIR}/js/chart.umd.min.js"

# Flatpickr (latest)
wget -q "https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/dark.css" \
    -O "${STATIC_DIR}/css/flatpickr-dark.css"
wget -q "https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.js" \
    -O "${STATIC_DIR}/js/flatpickr.min.js"
wget -q "https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/ru.js" \
    -O "${STATIC_DIR}/js/flatpickr-ru.js"

echo "Статические ресурсы загружены в ${STATIC_DIR}"

# ── 7. Systemd-сервис ─────────────────────────────────────────
echo ">>> [7/7] Создание systemd-сервиса ${SERVICE_NAME}..."

cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=МедДневник — Персональный медицинский дневник
After=network.target

[Service]
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${HOME}/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="HOME=${HOME}"
ExecStart=${UV_BIN} run ${PROJECT_DIR}/run.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}.service"
systemctl restart "${SERVICE_NAME}.service"

# ── Проверка ─────────────────────────────────────────────────
sleep 2
if systemctl is-active --quiet "${SERVICE_NAME}.service"; then
    echo ""
    echo "========================================"
    echo " Установка завершена успешно!"
    echo " Веб-интерфейс: http://$(hostname -I | awk '{print $1}'):${PORT}"
    echo " Управление сервисом:"
    echo "   systemctl status ${SERVICE_NAME}"
    echo "   systemctl restart ${SERVICE_NAME}"
    echo "   journalctl -u ${SERVICE_NAME} -f"
    echo "========================================"
    # Очистка временных файлов
    rm -rf "/tmp/${ARCHIVE_NAME}" "/tmp/med-dnevnik.tar.gz"
else
    echo ""
    echo "Ошибка: сервис не запустился."
    echo "Проверьте журнал: journalctl -u ${SERVICE_NAME} -b --no-pager"
    exit 1
fi
