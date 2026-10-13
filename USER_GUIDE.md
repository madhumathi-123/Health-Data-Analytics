# User Guide - Outbreak-Linked Smart Drug Inventory System

## 📖 Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard](#dashboard)
4. [Inventory Management](#inventory-management)
5. [Outbreak Predictions](#outbreak-predictions)
6. [Order Management](#order-management)
7. [Reports](#reports)
8. [User Roles & Permissions](#user-roles--permissions)

---

## Introduction

The **Outbreak-Linked Smart Drug Inventory System** is an AI-powered platform that:
- Predicts disease outbreaks using machine learning
- Manages medicine inventory automatically
- Tracks supply chain and orders
- Generates comprehensive reports
- Sends automated notifications

---

## Getting Started

### First Login

1. Open your browser and go to `http://localhost:3000`
2. Enter your credentials:
   - **Email:** admin@health.com
   - **Password:** admin123
3. Click **Login**

### Navigation

The system has 5 main sections accessible from the left sidebar:
- 🏠 **Dashboard** - Overview and statistics
- 📦 **Inventory** - Medicine management
- 📊 **Predictions** - Outbreak forecasts
- 🛒 **Orders** - Order tracking
- 📄 **Reports** - Analytics and exports

---

## Dashboard

### Overview Cards

The dashboard displays 4 key metrics:

1. **Total Medicines** - Number of medicines in inventory
2. **Low Stock Items** - Medicines below reorder level
3. **High Risk Predictions** - Outbreak alerts (≥70% probability)
4. **Pending Orders** - Orders awaiting processing

### Charts

- **Inventory Overview (Bar Chart)** - Visual breakdown of inventory status
- **Distribution (Pie Chart)** - Proportional view of system metrics

### Alerts

- **Critical Low Stock Items** - Top 5 medicines requiring immediate attention
- **Recent Outbreak Predictions** - Latest AI-generated forecasts

### Actions

- Click on any metric card to view details
- Hover over charts for specific values
- Click on list items to navigate to detailed views

---

## Inventory Management

### Viewing Medicines

1. Navigate to **Inventory** from sidebar
2. Use tabs to filter:
   - **All** - Complete inventory
   - **Low Stock** - Items below reorder level
   - **Adequate** - Items with sufficient stock

### Search & Filter

- Use the search bar to find medicines by name or disease
- Results update in real-time as you type

### Stock Status Indicators

- 🟢 **Good** - Stock > 150% of reorder level
- 🟡 **Adequate** - Stock between reorder level and 150%
- 🔴 **Low Stock** - Stock < reorder level

### Updating Stock

1. Click the **Edit** icon (✏️) on any medicine row
2. Enter new stock quantity
3. Click **Update**
4. System logs the change automatically

### Adding New Medicine

1. Click **Add Medicine** button
2. Fill in required fields:
   - Medicine Name
   - Disease
   - Current Stock
   - Reorder Level
   - Unit Price
   - Supplier
   - Expiry Date
3. Click **Save**

### Viewing Details

Each medicine row shows:
- Medicine Name
- Disease Treated
- Current Stock
- Reorder Level
- Unit Price (₹)
- Supplier
- Status Badge

---

## Outbreak Predictions

### Understanding Predictions

The AI system analyzes:
- Historical outbreak data
- Seasonal patterns
- Geographic trends
- Disease characteristics

### Running Predictions

1. Navigate to **Predictions**
2. Click **Run Prediction** button
3. Wait 30-60 seconds for AI processing
4. View results on map and list

### Risk Map

The interactive map shows:
- **Red Circles** - High risk (≥70%)
- **Orange Circles** - Medium risk (50-70%)
- **Yellow Circles** - Low risk (<50%)

**Circle Size** = Risk Score

### Viewing Prediction Details

Click on any map marker to see:
- Location and State
- Risk Score
- Total Expected Cases
- Number of Predictions
- Disease Breakdown

### High Risk Alerts

The right panel shows critical predictions:
- Disease Name
- Location
- Probability Percentage
- Expected Cases
- Severity Level
- Predicted Date

### Severity Levels

- 🔴 **Critical** - Immediate action required
- 🟠 **High** - Prepare resources
- 🔵 **Medium** - Monitor situation
- ⚪ **Low** - Standard precautions

### Taking Action

When high-risk prediction appears:
1. Review medicine inventory for that disease
2. Check stock levels
3. Create orders if needed
4. Coordinate with suppliers
5. Notify relevant authorities

---

## Order Management

### Viewing Orders

Orders are organized in tabs:
- **All** - Complete order history
- **Pending** - Awaiting confirmation
- **In Progress** - Confirmed or Shipped
- **Delivered** - Completed orders

### Creating New Order

1. Click **Create Order** button
2. Select:
   - **Medicine** - From dropdown list
   - **Supplier** - From available suppliers
   - **Quantity** - Number of units
   - **Notes** - Optional details
3. Click **Create Order**

### Order Workflow

```
Pending → Confirmed → Shipped → Delivered
```

### Updating Order Status

**For Pending Orders:**
- Click **Confirm** to approve order

**For Confirmed Orders:**
- Click **Ship** when dispatched

**For Shipped Orders:**
- Click **Deliver** when received

### Order Information

Each order displays:
- Order ID (unique identifier)
- Medicine Name
- Supplier
- Quantity
- Order Date
- Expected Delivery Date
- Total Cost (₹)
- Current Status

### Automatic Stock Update

When order status changes to **Delivered**:
- Medicine stock automatically increases
- Inventory updated in real-time
- Audit log created

---

## Reports

### Available Reports

#### 1. Inventory Report
**Formats:** PDF, Excel

**Contains:**
- Complete medicine list
- Stock levels and values
- Low stock alerts
- Expiry information
- Supplier details
- Total inventory value

**Use Cases:**
- Monthly inventory review
- Audit compliance
- Budget planning

#### 2. Outbreak History Report
**Format:** PDF

**Contains:**
- Historical outbreak data
- AI predictions
- Risk assessments
- Trend analysis
- Geographic distribution

**Use Cases:**
- Epidemic preparedness
- Resource allocation
- Policy making

#### 3. Orders Report
**Format:** Excel

**Contains:**
- Complete order history
- Supplier performance
- Delivery timelines
- Cost analysis
- Status breakdown

**Use Cases:**
- Supplier evaluation
- Budget tracking
- Process optimization

### Downloading Reports

1. Navigate to **Reports**
2. Select desired report card
3. Click **Download PDF** or **Download Excel**
4. File downloads automatically
5. Open with appropriate application

### Generate All Reports

Click **Generate All Reports** to create all reports simultaneously.

### Report Naming

Reports are automatically named with timestamp:
- `inventory_report_2024-11-10.pdf`
- `outbreak_report_2024-11-10.pdf`
- `orders_report_2024-11-10.xlsx`

---

## User Roles & Permissions

### Admin
**Full Access** - All features and settings

**Can:**
- Manage all inventory
- Run predictions
- Create/approve orders
- Generate reports
- Manage users
- View audit logs
- Delete records

### Manager
**Management Access** - Operations and oversight

**Can:**
- View and update inventory
- Run predictions
- Create and approve orders
- Generate reports
- View notifications

**Cannot:**
- Delete records
- Manage users
- Access audit logs

### Staff
**Operational Access** - Daily operations

**Can:**
- View inventory
- Update stock levels
- View orders
- View predictions

**Cannot:**
- Create orders
- Run predictions
- Delete records
- Generate reports

### Viewer
**Read-Only Access** - View information only

**Can:**
- View dashboard
- View inventory
- View predictions
- View reports

**Cannot:**
- Modify any data
- Create orders
- Update stock

---

## Best Practices

### Daily Tasks

1. **Check Dashboard** - Review alerts and metrics
2. **Monitor Low Stock** - Address critical items
3. **Review Predictions** - Prepare for potential outbreaks
4. **Process Orders** - Update order statuses

### Weekly Tasks

1. **Run Predictions** - Generate new forecasts
2. **Review Inventory** - Check expiring medicines
3. **Supplier Performance** - Evaluate delivery times
4. **Generate Reports** - Weekly analytics

### Monthly Tasks

1. **Comprehensive Reports** - Full system analysis
2. **Stock Audit** - Verify physical inventory
3. **Budget Review** - Analyze costs
4. **System Optimization** - Review workflows

---

## Tips & Tricks

### Keyboard Shortcuts

- **Ctrl + F** - Search in current page
- **Esc** - Close dialogs
- **Tab** - Navigate form fields

### Quick Actions

- Double-click table rows for details
- Use filters to find specific items quickly
- Bookmark frequently used pages

### Performance

- Refresh data regularly for latest information
- Close unused browser tabs
- Clear browser cache if experiencing slowness

---

## Troubleshooting

### Can't Login?
- Verify email and password
- Check CAPS LOCK is off
- Try default credentials from setup guide

### Data Not Loading?
- Check internet connection
- Refresh the page (F5)
- Verify backend server is running

### Predictions Not Working?
- Ensure ML models are trained
- Check backend logs for errors
- Verify sufficient data exists

### Reports Not Downloading?
- Check browser download settings
- Disable popup blockers
- Try different browser

---

## Support & Help

### Getting Help

1. Check this user guide
2. Review SETUP_GUIDE.md
3. Check error messages in browser console (F12)
4. Review backend logs

### Common Issues

**Issue:** "Network Error"
- **Solution:** Ensure backend is running on port 5000

**Issue:** "Unauthorized"
- **Solution:** Login again, token may have expired

**Issue:** "Failed to load data"
- **Solution:** Refresh page, check database connection

---

## Glossary

- **Outbreak** - Sudden increase in disease cases
- **Prediction** - AI-generated forecast
- **Risk Score** - Probability × Severity (0-100)
- **Reorder Level** - Minimum stock before ordering
- **Lead Time** - Days from order to delivery
- **Stock Status** - Current inventory health
- **Severity Level** - Outbreak impact classification

---

**For technical support, refer to SETUP_GUIDE.md or contact your system administrator.**
