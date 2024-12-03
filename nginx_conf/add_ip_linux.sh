#!/bin/bash

# Получение IP-адреса компьютера
IP_ADDRESS=$(hostname -I | awk '{print $1}')

# Добавление IP-адреса и доменного имени в /etc/hosts
echo "$IP_ADDRESS brain-flow.com" | sudo tee -a /etc/hosts > /dev/null

echo "Запись добавлена: $IP_ADDRESS brain-flow.com"
