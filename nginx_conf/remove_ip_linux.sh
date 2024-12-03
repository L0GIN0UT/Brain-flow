#!/bin/bash

# Получение IP-адреса компьютера
IP_ADDRESS=$(hostname -I | awk '{print $1}')

# Удаление строки, содержащей IP-адрес и доменное имя из /etc/hosts
sudo sed -i "/$IP_ADDRESS brain-flow.com/d" /etc/hosts

echo "Запись удалена: $IP_ADDRESS brain-flow.com"
