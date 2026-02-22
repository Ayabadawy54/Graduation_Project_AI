# 🚀 TalentTree Admin Dashboard API — Complete Documentation
> **Version:** 2.0.0 | **Total Endpoints:** 52 | **Last Updated:** 2026-02-22  
> **Base URL (Docker):** `http://localhost:8000`  
> **Interactive Docs:** `http://localhost:8000/docs`

---

## 📦 Modules Overview

| # | Module | Tag | Endpoints | Base Path |
|---|---|---|---|---|
| 1 | Dashboard | Dashboard | 2 | `/api/admin/dashboard` |
| 2 | Brands | Brands | 3 | `/api/admin/brands` |
| 3 | Products | Products | 6 | `/api/admin/products` |
| 4 | Orders | Orders | 6 | `/api/admin/orders` |
| 5 | Analytics | Analytics | 5 | `/api/admin/analytics` |
| 6 | Customers & Users | Customers & Users | 7 | `/api/admin/customers`, `/api/admin/users` |
| 7 | Vendors & Materials | Vendors & Materials | 4 | `/api/admin/vendors`, `/api/admin/raw-materials` |
| 8 | Support | Support | 3 | `/api/admin/support-tickets` |
| 9 | **Payments** 🆕 | Payments | 4 | `/api/admin/payments` |
| 10 | **Reports** 🆕 | Reports | 3 | `/api/admin/reports` |
| 11 | **Notifications** 🆕 | Notifications | 3 | `/api/admin/notifications` |
| 12 | **Admin Actions Log** 🆕 | Admin Actions Log | 2 | `/api/admin/admin-actions` |
| 13 | **Inventory** 🆕 | Inventory | 3 | `/api/admin/inventory` |
| — | Core | — | 2 | `/` `/health` |
| | **TOTAL** | | **52** | |

---

## 📡 All Endpoints

### 1. Dashboard
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/dashboard/overview` | Platform metrics + AI alerts + recommendations |
| GET | `/api/admin/dashboard/category-performance` | Sales by category |

### 2. Brands
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/brands` | List brands (filters: category, risk_level, verified) |
| GET | `/api/admin/brands/{brand_id}` | Brand detail + AI risk insights |
| GET | `/api/admin/brands/analytics/risk-analysis` | All high/medium risk brands |

### 3. Products
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/products` | List products (filters: status, category, brand_id) |
| GET | `/api/admin/products/pending-approval` | Queue with AI quality scores |
| GET | `/api/admin/products/analytics/trending` | Top trending by views+clicks score |
| GET | `/api/admin/products/analytics/pricing-analysis` | Price ranges by category |
| GET | `/api/admin/products/{product_id}` | Product detail + quality assessment |
| POST | `/api/admin/products/{product_id}/approve` | Approve or reject product |

### 4. Orders
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/orders` | List orders (filters: status, date range) |
| GET | `/api/admin/orders/analytics/forecast` | AI order volume forecast (next N days) |
| GET | `/api/admin/orders/analytics/late-fulfillment` | Orders at risk of late delivery |
| GET | `/api/admin/orders/analytics/by-governorate` | Order heatmap by Egyptian governorate |
| GET | `/api/admin/orders/analytics/anomalies` | Spike + cancellation rate detection |
| GET | `/api/admin/orders/{order_id}` | Single order detail |

### 5. Analytics
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/analytics/sales-trends?period=30` | Daily sales over N days |
| GET | `/api/admin/analytics/revenue-breakdown` | Revenue by category & governorate |
| GET | `/api/admin/analytics/conversion-funnel` | Views → Clicks → Favorites → Purchases |
| GET | `/api/admin/analytics/reports/weekly?week_offset=0` | Weekly report (0=current, 1=last week…) |
| GET | `/api/admin/analytics/category-deep-dive/{category}` | Deep category analysis |

### 6. Customers & Users
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/users` | All platform users (owners + customers) |
| GET | `/api/admin/users/analytics/overview` | User growth, breakdown by type/governorate |
| PUT | `/api/admin/users/{user_id}/status?action=suspend` | Suspend or activate user |
| DELETE | `/api/admin/users/{user_id}` | Soft-delete user |
| GET | `/api/admin/customers` | Customers list with AI segments |
| GET | `/api/admin/customers/analytics/segments` | VIP / Loyal / Occasional / At Risk counts |
| GET | `/api/admin/customers/{customer_id}` | Customer detail + spend + segment |

### 7. Vendors & Materials
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/vendors` | All raw material vendors |
| GET | `/api/admin/vendors/{vendor_id}` | Vendor detail + performance |
| GET | `/api/admin/raw-materials` | Material catalog |
| GET | `/api/admin/raw-materials/demand-forecast` | Top 20 most demanded materials |

### 8. Support
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/support-tickets` | List tickets (filters: status, priority) |
| GET | `/api/admin/support-tickets/analytics/summary` | Counts by status/priority/category |
| GET | `/api/admin/support-tickets/{ticket_id}` | Single ticket detail |

### 9. Payments 🆕
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/payments` | List payments (filters: status, method, days) |
| GET | `/api/admin/payments/analytics/summary` | Revenue by method, success rate |
| GET | `/api/admin/payments/analytics/trends` | Daily payment volume over time |
| GET | `/api/admin/payments/{payment_id}` | Single payment + linked order |

### 10. Reports 🆕
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/reports/monthly?year=2026&month=2` | Full monthly report |
| GET | `/api/admin/reports/brands/{brand_id}` | Per-brand performance report |
| GET | `/api/admin/reports/export/summary` | Platform summary for PDF/Excel export |

### 11. Notifications 🆕
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/notifications` | All live notifications from platform state |
| GET | `/api/admin/notifications/count` | Unread count for frontend badge |
| POST | `/api/admin/notifications/{id}/read` | Mark notification as read |

> 💡 Notifications are generated **dynamically** (no CSV) from: pending approvals, high-risk brands, order anomalies, and critical low stock.

### 12. Admin Actions Log 🆕
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/admin-actions` | Action log (filters: action_type, admin_user_id, target_type) |
| GET | `/api/admin/admin-actions/analytics` | Actions summary by type, admin, month |

### 13. Inventory 🆕
| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/inventory/overview` | Stock health (out of stock, low, healthy) |
| GET | `/api/admin/inventory/low-stock?threshold=10` | Products below stock threshold |
| GET | `/api/admin/inventory/analytics` | Stock value, top stocked, urgent restock list |

---

## 🤖 AI Features

| Feature | Where Used | Logic |
|---|---|---|
| Brand Risk Score | brands, dashboard | `cancellation × 0.4 + (1−fulfillment) × 0.3 + (5−rating)/5 × 0.2 + (0.1 if unverified)` |
| Product Quality Score | products/pending-approval | Price range + stock + description length + brand reputation |
| Sales Forecasting | orders/forecast | Moving average × day-of-week multiplier (Fri/Sat ×1.2) |
| Customer Segmentation | customers | VIP / Loyal / Occasional / At Risk / New Customer |
| Anomaly Detection | orders/anomalies, notifications | Statistical z-score on daily order volumes |
| Restock Urgency | inventory/analytics | `sales_count / stock_quantity` ratio |

---

## 🗄️ Data Sources (CSV Files)

| File | Records | Used By |
|---|---|---|
| `users.csv` | 600 | customers, users |
| `brands.csv` | 100 | brands, dashboard |
| `products.csv` | 500 | products, inventory |
| `orders.csv` | 2,000 | orders, analytics, dashboard |
| `payments.csv` | 2,000 | payments |
| `reviews.csv` | 400 | brands (sentiment) |
| `static_vendors.csv` | 10 | vendors |
| `raw_material_marketplace.csv` | 50 | vendors |
| `material_requests.csv` | 200 | vendors |
| `support_tickets.csv` | 150 | support |
| `admin_actions.csv` | 200 | admin-actions |
| `analytics_snapshots.csv` | 180 | analytics |

---

## 📁 Project Structure

```
api/
├── endpoints/
│   ├── dashboard.py       ✅ Dashboard metrics
│   ├── brands.py          ✅ Brand management & risk
│   ├── products.py        ✅ Product mgmt & quality
│   ├── orders.py          ✅ Order management & forecasting
│   ├── analytics.py       ✅ Sales analytics & reports
│   ├── customers.py       ✅ Customer + user management
│   ├── vendors.py         ✅ Vendor & materials
│   ├── support.py         ✅ Support tickets
│   ├── payments.py        🆕 Payment analytics
│   ├── reports.py         🆕 Report generation
│   ├── notifications.py   🆕 Live notification system
│   ├── admin_actions.py   🆕 Admin audit log
│   └── inventory.py       🆕 Inventory management
├── services/
│   ├── data_service.py    ✅ CSV data access layer
│   └── ai_service.py      ✅ All AI algorithms
└── models/
    └── schemas.py         ✅ Pydantic validation models
```

---

## 🚀 Running with Docker

```powershell
# Start all containers
docker-compose up -d

# Check health
docker ps

# View logs
docker logs talentree-api --tail 50
```

**Services:**
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Jupyter: `http://localhost:8888`

---

## 🔍 Example Requests

```bash
# Dashboard
curl http://localhost:8000/api/admin/dashboard/overview

# Payments summary
curl http://localhost:8000/api/admin/payments/analytics/summary

# Notifications (live)
curl http://localhost:8000/api/admin/notifications

# Monthly report for February 2026
curl "http://localhost:8000/api/admin/reports/monthly?year=2026&month=2"

# Inventory critical stock
curl http://localhost:8000/api/admin/inventory/low-stock?threshold=5

# Weekly report — last week
curl "http://localhost:8000/api/admin/analytics/reports/weekly?week_offset=1"

# Pending product approvals
curl http://localhost:8000/api/admin/products/pending-approval

# Admin audit log
curl http://localhost:8000/api/admin/admin-actions?action_type=verify_brand
```

---

## ⚠️ Developer Notes

> **FastAPI Route Ordering Rule:** Always register static/named routes **before** dynamic `/{id}` routes.  
> Example: `/products/pending-approval` must come before `/products/{product_id}`.  
> All endpoints in this project follow this rule correctly.

---

**Status:** ✅ Production-Ready | **Version:** 2.0.0 | **Updated:** 2026-02-22
