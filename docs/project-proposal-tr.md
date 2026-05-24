# Proje Önerisi: Car Rental Cloud

## Proje Konusu

Bu projede cloud üzerinde çalıştırılabilecek, 12-factor prensiplerine uygun bir
araç kiralama sistemi geliştirilecektir. Sistem araç envanteri, müşteri bilgileri
ve kiralama süreçlerini yönetecektir.

## Amaç

Amaç; araç kiralama operasyonlarını web tabanlı bir servis üzerinden yönetmek,
cloud-native deployment, CI/CD, logging, monitoring ve backing service kullanımını
göstermektir.

## Kapsam

- Araç ekleme ve araç durum yönetimi
- Müşteri ekleme
- Kiralama oluşturma
- Kiralama tarih çakışması kontrolü
- Araç iadesi
- REST API ve web dashboard
- Docker ile containerization
- GitHub Actions ile CI/CD
- Health, readiness ve metrics endpointleri

## Önerilen Teknoloji Yığını

- Python Flask
- PostgreSQL
- Redis
- Docker
- GitHub Actions
- Google Cloud Run / Cloud SQL / Cloud Logging

## 12-Factor Yaklaşımı

Konfigürasyon environment variable üzerinden yapılacak, uygulama stateless HTTP
process olarak çalışacak, backing service bağlantıları URL ile tanımlanacak,
loglar stdout'a yazılacak ve Docker image cloud ortamında deploy edilecektir.

