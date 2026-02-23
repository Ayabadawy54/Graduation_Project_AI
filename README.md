---
title: Talentree Admin API
emoji: 🛍️
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
license: mit
short_description: AI-powered admin dashboard API for Talentree Egyptian marketplace
---

# 🛍️ TalentTree Admin Dashboard API

AI-powered FastAPI backend for the TalentTree Egyptian handmade marketplace admin dashboard.

## 🚀 API Base URL

```
https://huggingface.co/spaces/YOUR_USERNAME/talentree-admin-api
```

## 📡 Key Endpoints

| Module | Path |
|---|---|
| Dashboard | `/api/admin/dashboard/overview` |
| Brands | `/api/admin/brands` |
| Products | `/api/admin/products` |
| Orders | `/api/admin/orders` |
| Analytics | `/api/admin/analytics/sales-trends` |
| Payments | `/api/admin/payments/analytics/summary` |
| Inventory | `/api/admin/inventory/overview` |
| Reports | `/api/admin/reports/monthly` |
| Notifications | `/api/admin/notifications` |

## 📚 Interactive Docs

Visit `/docs` for the full Swagger UI with all **52 endpoints**.

## 🤖 AI Features

- Brand risk scoring
- Product quality assessment
- Sales forecasting
- Customer segmentation
- Anomaly detection

## 🛠️ Tech Stack

- **FastAPI** + Uvicorn
- **Pandas** for data processing
- **Python 3.10**
- Deployed via Docker on Hugging Face Spaces
