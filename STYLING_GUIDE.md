# Frontend UI Styling Guide

## Overview
The ABA Security Oracle dashboard features a professional dark theme with blue accents, designed for security operations centers.

---

## COLOR PALETTE

### Primary Colors
- **Dark Background**: `#0e1117` - Main dashboard background
- **Primary Blue**: `#1f77b4` - Headers, borders, highlights
- **Dark Blue**: `#0055aa` - Card backgrounds, active states
- **Light Gray**: `#888` - Secondary text

### Risk Level Colors
- **🔴 CRITICAL**: `#da3633` - Red, immediate action needed
- **🟠 HIGH**: `#fb8500` - Orange, increased vigilance
- **🟡 MEDIUM**: `#fbbf24` - Amber, standard monitoring
- **🟢 LOW**: `#10b981` - Green, stable condition

### Chat Colors
- **User Messages**: `#1f77b4` (blue) - User's queries
- **AI Messages**: `#238636` (green) - System's responses
- **Chat Border**: `#30363d` - Container borders
- **Dark Container**: `#161b22` - Chat background

---

## CSS CLASSES & STYLING

### `.main-header`
```css
font-size: 3rem;
color: #1f77b4;
text-align: center;
margin-bottom: 0.5rem;
font-weight: bold;
text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
```
**Usage**: Main dashboard title
**Result**: Large centered blue title with subtle shadow

---

### `.subtitle`
```css
text-align: center;
color: #888;
margin-bottom: 2rem;
font-size: 1.1rem;
```
**Usage**: Secondary title under main header
**Result**: Centered gray text for location info

---

### `.metric-card`
```css
background: linear-gradient(135deg, #1f77b4 0%, #0055aa 100%);
padding: 1.5rem;
border-radius: 0.8rem;
margin-bottom: 1rem;
color: white;
box-shadow: 0 4px 6px rgba(0,0,0,0.3);
```
**Usage**: Quick stats display (Total Incidents, Critical Cases, etc.)
**Result**: Blue gradient cards with shadow depth

---

### `.tab-header`
```css
font-size: 1.3rem;
font-weight: bold;
color: #1f77b4;
padding: 1rem;
border-bottom: 2px solid #1f77b4;
margin-bottom: 1.5rem;
```
**Usage**: Tab section titles (Overview, Hotspots, etc.)
**Result**: Bold blue header with underline accent

---

### `.chat-container`
```css
background-color: #161b22;
border: 1px solid #30363d;
border-radius: 0.8rem;
padding: 1rem;
margin: 0.5rem 0;
```
**Usage**: Overall chat message container
**Result**: Dark gray box with subtle border

---

### `.chat-user`
```css
background-color: #1f77b4;
padding: 1rem;
border-radius: 0.6rem;
margin: 0.5rem 0;
color: white;
border-left: 4px solid #0055aa;
```
**Usage**: User query display
**Result**: Blue message bubble with left border accent

---

### `.chat-ai`
```css
background-color: #238636;
padding: 1rem;
border-radius: 0.6rem;
margin: 0.5rem 0;
color: white;
border-left: 4px solid #1a7f37;
```
**Usage**: AI response display
**Result**: Green message bubble with left border accent

---

### `.risk-critical`
```css
background-color: #da3633;
color: white;
padding: 0.5rem 1rem;
border-radius: 0.4rem;
font-weight: bold;
```
**Usage**: CRITICAL risk badge
**Result**: Red badge with bold text

---

### `.risk-high`
```css
background-color: #fb8500;
color: white;
padding: 0.5rem 1rem;
border-radius: 0.4rem;
font-weight: bold;
```
**Usage**: HIGH risk badge
**Result**: Orange badge with bold text

---

### `.risk-medium`
```css
background-color: #fbbf24;
color: black;
padding: 0.5rem 1rem;
border-radius: 0.4rem;
font-weight: bold;
```
**Usage**: MEDIUM risk badge
**Result**: Amber badge with bold text (black text for contrast)

---

### `.risk-low`
```css
background-color: #10b981;
color: white;
padding: 0.5rem 1rem;
border-radius: 0.4rem;
font-weight: bold;
```
**Usage**: LOW risk badge
**Result**: Green badge with bold text

---

### `.divider`
```css
border-top: 2px solid #30363d;
margin: 2rem 0;
```
**Usage**: Visual section separators
**Result**: Horizontal line separating major sections

---

## LAYOUT STRUCTURE

### Main Page Layout
```
┌─────────────────────────────────────────┐
│         Header Section (Centered)        │
│      🛡️ ABA Security Oracle              │
│   Real-time Security Analysis for Aba    │
│─────────────────────────────────────────│
│   [Metric1]  [Metric2]  [Metric3] [M4]  │
├─────────────────────────────────────────┤
│ ┌─┬─────────┬─────────┬─────────┬─────┐ │
│ │📊│ 📊 Overview │ 🔍 Hot │ 📈 Trends │ │
│ │Si│ 🔍 Hotspots │ spots  │ ⚠️ Risk  │ │
│ │de│ 📈 Trends   │ 📈 Tre │ 💬 AI    │ │
│ │ba│ ⚠️ Risk     │ nds    │          │ │
│ │r │ 💬 AI Chat  │ ⚠️ Ris │          │ │
│ └─┴─────────┴─────────┴─────────┴─────┘ │
│                                         │
│        [Tab Content Goes Here]          │
│                                         │
└─────────────────────────────────────────┘
```

### Sidebar Configuration
```
┌─────────────────────┐
│  ⚙️ Configuration    │
│────────────────────│
│ 📍 Location: Aba   │
│                    │
│ Clustering Radius  │
│ [====|=====] 0.5km │
│                    │
│ Min Incidents      │
│ [======|==] 3      │
│────────────────────│
│ ☑ Use Demo Data    │
│ Incidents: [==|=]  │
│────────────────────│
│ 💡 Tip: Use AI...  │
└─────────────────────┘
```

### Chat Interface Layout
```
┌─────────────────────────────────────────┐
│         Conversation History             │
│─────────────────────────────────────────│
│ 👤 You: What about Brass Road?         │  ← Blue
│                                         │
│ 🤖 AI: SECURITY PROFILE: BRASS ROAD   │  ← Green
│        ...detailed analysis...          │
│─────────────────────────────────────────│
│ [Text Input Field]              [Send] │
│─────────────────────────────────────────│
│ 💡 Example Queries:                    │
│    - "What is the security situation..." │
│    - "Show me all critical risk areas" │
└─────────────────────────────────────────┘
```

---

## RESPONSIVE DESIGN

### Multi-Column Layouts
```python
# Header (3 columns with center emphasis)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<p class="main-header">...</p>')

# Metrics (4 equal columns)
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total Incidents", 1247)

# Chat input (5:1 split)
col1, col2 = st.columns([5, 1])
with col1: user_input = st.text_input(...)
with col2: send_button = st.button("🚀 Send")
```

---

## ICONS & EMOJIS

### Tab Icons
- `📊` Overview - Dashboard/statistics
- `🔍` Hotspots - Search/detective
- `📈` Trends - Graph/analytics
- `⚠️` Risk - Warning/alert
- `💬` AI Analysis - Chat/dialog

### UI Elements
- `🛡️` Security - Main logo
- `🚀` Send - Action button
- `🔍` Analysis - Detail search
- `⚙️` Configuration - Settings
- `📍` Location - Place marker
- `💡` Tip - Information hint
- `👤` User - Person/you
- `🤖` AI - Robot/system

---

## TYPOGRAPHY

### Font Sizes
- **Main Header** (h1): 3rem - Bold, centered
- **Tab Header** (h2): 1.3rem - Bold, with underline
- **Subtitle**: 1.1rem - Gray, secondary info
- **Body Text**: 1rem - Default

### Font Weights
- **Bold**: Headers, section titles, badges
- **Regular**: Body text, descriptions

---

## SPACING & PADDING

- **Section Margins**: 2rem (top/bottom)
- **Card Padding**: 1.5rem
- **Component Margin**: 0.5rem
- **Header Bottom Margin**: 0.5rem

---

## SHADOW & DEPTH

- **Card Shadow**: `0 4px 6px rgba(0,0,0,0.3)` - Subtle depth
- **Text Shadow**: `2px 2px 4px rgba(0,0,0,0.3)` - Header only
- **Border Styles**: 1-2px solid borders in dark gray

---

## INTERACTIVE ELEMENTS

### Buttons
```python
st.button("🚀 Send", use_container_width=True)
# Streamlit default button styling with emoji
```

### Input Fields
```python
st.text_input(
    "Ask about security in ABA:",
    placeholder="E.g., What is the security situation...",
    key="user_input"
)
# Follows Streamlit input styling
```

### Sliders
```python
st.slider(
    "Clustering Radius (km)",
    0.1, 2.0, 0.5,
    help="Distance threshold for grouping incidents"
)
# With helpful tooltips
```

---

## ACCESSIBILITY FEATURES

1. **Color Contrast**: All text has sufficient contrast
2. **Semantic Structure**: Proper header hierarchy
3. **Clear Labels**: All inputs have descriptive labels
4. **Icon + Text**: Icons paired with text labels
5. **Help Text**: Tooltips on configuration options
6. **Example Queries**: Guidance for new users

---

## CUSTOMIZATION GUIDE

### Changing Colors
Modify these in the CSS `<style>` block:
```css
/* Change primary blue accent */
--primary: #1f77b4;

/* Change risk level colors */
.risk-critical { background-color: #YOUR_COLOR; }
```

### Adjusting Spacing
```python
st.markdown('<div style="margin-top: 2rem;"></div>')
```

### Adding New Risk Levels
```python
# Add to CSS
.risk-extreme {
    background-color: #YOUR_COLOR;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.4rem;
    font-weight: bold;
}

# Use in code
st.markdown('<span class="risk-extreme">EXTREME</span>')
```

---

## BROWSER COMPATIBILITY

- ✅ Chrome/Chromium (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers (with responsive design)

---

## PERFORMANCE NOTES

- Light theme: Uses system dark mode for reduced eye strain
- CSS is embedded (no external dependencies)
- Streamlit handles responsive design automatically
- Custom CSS adds minimal performance overhead

---

**Last Updated**: 2024-11-24
**Status**: Production Ready
