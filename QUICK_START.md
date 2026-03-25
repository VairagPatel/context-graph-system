# 🚀 Quick Start Guide

## Get Running in 60 Seconds

### 1. Get a Free Groq API Key
```
1. Visit: https://console.groq.com
2. Sign up (no credit card needed)
3. Go to "API Keys" → "Create API Key"
4. Copy your key (starts with gsk_)
```

### 2. Start the Server
```bash
npm install      # Install dependencies
npm run build    # Build frontend
npm start        # Start server on port 3001
```

### 3. Open the App
```
Navigate to: http://localhost:3001
Enter your Groq API key when prompted
```

---

## 🎮 New Features Guide

### Graph Controls (Top-Left Toolbar)

**👁 Toggle Edges**
- Click to show/hide all graph connections
- Useful for focusing on node positions without visual clutter

**⚡ Toggle Physics**
- Enable: Nodes move dynamically (force simulation active)
- Disable: Freeze layout in current position
- Tip: Disable after layout stabilizes for better performance

**🔄 Reset Layout**
- Reheats the force simulation
- Reorganizes nodes from current positions
- Use when graph becomes messy

**⊡ Zoom Fit**
- Fits all nodes in viewport
- Auto-adjusts zoom level
- Centers the graph

### Node Interactions

**Single Click**
- Opens node inspector panel (left side)
- Shows all metadata fields grouped by category
- For billing documents: Shows "Trace Full O2C Flow" button

**Double Click**
- Highlights the clicked node + all neighbors
- Zooms to 2.5x centered on node
- Great for exploring local neighborhoods

**Search (Top-Right)**
- Type to filter nodes by label, type, or ID
- Matching nodes are highlighted in amber
- Shows match count badge

### Chat Interface

**Natural Language Queries**
```
Examples:
- "Show me the top 10 products by billing volume"
- "Which deliveries haven't been billed yet?"
- "Trace billing document 90504248"
- "What's the total payment amount per customer?"
```

**Features:**
- 10-turn conversation memory
- SQL disclosure (click to expand)
- Results table with pagination
- Node highlighting (12 seconds)
- Off-topic rejection

### Anomaly Detection Tab

**Proactive Issue Detection:**
- 🔴 Critical: Deliveries not billed, Billed without journal entry
- 🟡 Warning: Open AR, Cancelled billing docs
- 🔵 Info: Orders without delivery

**Click any anomaly to:**
- Run the detection SQL
- Highlight affected nodes
- View detailed results

---

## 🎨 Visual Guide

### Node Colors
- **Blue (solid)**: Customer, Sales Order
- **Purple**: Journal Entry
- **Green (ring)**: Delivery
- **Amber (ring)**: Billing Document
- **Orange (ring)**: Payment
- **Red (ring)**: Product
- **Light Blue**: Plant

### Highlight Colors
- **Green glow**: Query results
- **Amber glow**: Search matches
- **Indigo glow**: Flow trace
- **Red glow**: Anomaly detection

### Edge Opacity
- Default: 0.15 (subtle)
- Arrows: 0.4 (slightly more visible)
- Tip: Toggle edges off for cleaner view

---

## 💡 Pro Tips

### 1. Explore O2C Flows
```
1. Click any Billing Document node
2. Click "Trace Full O2C Flow" button
3. See the complete chain: Customer → Order → Delivery → Billing → Journal → Payment
```

### 2. Find Broken Flows
```
1. Go to Anomaly Detection tab
2. Click "Deliveries Not Billed" (critical)
3. See which deliveries are missing invoices
4. Nodes are highlighted in red
```

### 3. Custom SQL Queries
```
1. Go to SQL Query tab
2. Use canned queries or write your own
3. Results appear in table below
4. Matching nodes light up on graph
```

### 4. Optimize Graph Layout
```
1. Let physics run for ~2 seconds
2. Click "Toggle Physics" to freeze
3. Use "Zoom Fit" to center
4. Double-click nodes to explore neighborhoods
```

### 5. Clean Up Visual Clutter
```
1. Click "Toggle Edges" to hide connections
2. Focus on node positions and clusters
3. Use search to find specific entities
4. Re-enable edges when needed
```

---

## 🔧 Troubleshooting

### "Invalid API key" Error
- Ensure key starts with `gsk_`
- Get new key at console.groq.com
- Check for extra spaces when pasting

### Graph Not Loading
- Check browser console for errors
- Ensure server is running on port 3001
- Try hard refresh (Ctrl+Shift+R)

### Slow Performance
- Disable physics after layout stabilizes
- Hide edges if not needed
- Close node inspector panel when done

### Chat Not Responding
- Check API key is entered
- Verify server logs for errors
- Groq free tier: 30 req/min limit

---

## 📊 Sample Queries to Try

### Business Intelligence
```
"What are the top 5 customers by total payment amount?"
"Show me all cancelled billing documents"
"Which plants have the most deliveries?"
```

### Process Analysis
```
"Find sales orders that were delivered but not billed"
"Show me billing documents without journal entries"
"What's the average time between order and delivery?"
```

### Specific Traces
```
"Trace the full flow for billing document 90504248"
"Show me all transactions for customer 17100001"
"What products are in sales order 1000"
```

### Data Quality
```
"Find orders with no delivery"
"Show me journal entries without payments"
"Which billing documents are still open?"
```

---

## 🎯 Keyboard Shortcuts

- **Enter** (in search): Focus first match
- **Enter** (in chat): Send message
- **Escape**: Close panels
- **Click + Drag**: Pan graph
- **Scroll**: Zoom in/out

---

## 📈 Performance Metrics

### Expected Response Times
- Graph load: ~1-2 seconds
- SQL query: ~50-200ms
- LLM response: ~0.5-1 second (Groq)
- Node highlight: Instant

### Capacity
- Current: ~200 nodes, ~300 links
- Recommended max: 500 nodes (with physics disabled)
- Large datasets: Use SQL filters to reduce result set

---

## 🌟 Best Practices

1. **Start with Anomaly Detection** - Get immediate insights
2. **Use Canned Queries** - Learn the schema structure
3. **Freeze Physics** - After layout stabilizes for better interaction
4. **Double-Click Exploration** - Discover node neighborhoods
5. **Conversation Context** - Ask follow-up questions naturally

---

## 🆘 Need Help?

- Check `MIGRATION_GUIDE.md` for technical details
- Review `README.md` for architecture overview
- Inspect browser console for errors
- Check server logs for API issues

---

**Enjoy exploring your SAP O2C data! 🎉**
