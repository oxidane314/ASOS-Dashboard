import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ASOS Inventory Analytics",
    page_icon="🛍️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Data loading & processing (mirrors the notebook logic) ────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, on_bad_lines="skip")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    df["description"] = df["description"].astype(str)

    def get_brand(text):
        if "by " in text:
            try:
                return text.split("by ")[1].split(" ")[0]
            except Exception:
                return "Unknown"
        return "Unknown"

    brand_map = {
        "New": "New Look",
        "River": "River Island",
        "Miss": "Miss Selfridge",
        "TopshopWelcome": "Topshop",
    }
    df["brand_raw"] = df["description"].apply(get_brand)
    df["Brand"] = df["brand_raw"].map(brand_map).fillna(df["brand_raw"])

    brand_counts = df["Brand"].value_counts()
    valid_brands = brand_counts[brand_counts > 5].index
    df = df[df["Brand"].isin(valid_brands)].copy()

    def stockout_metrics(size_str):
        if not isinstance(size_str, str):
            return 0, 0.0
        sizes = size_str.split(",")
        total = len(sizes)
        oos = size_str.count("Out of stock")
        return oos, oos / total if total > 0 else 0.0

    metrics = df["size"].apply(stockout_metrics)
    df["Stockout_Count"] = [x[0] for x in metrics]
    df["Stockout_Rate"] = [x[1] for x in metrics]
    df["Lost_Revenue"] = df["Stockout_Count"] * df["price"]
    return df


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🔍 Filters")
uploaded = st.sidebar.file_uploader("Upload products_asos.csv", type="csv")

if uploaded:
    import io
    raw = uploaded.read()
    df_full = load_data(io.StringIO(raw.decode("utf-8", errors="replace")))
else:
    st.info("👈 Upload **products_asos.csv** in the sidebar to get started.")
    st.stop()

all_brands = sorted(df_full["Brand"].unique())
selected_brands = st.sidebar.multiselect(
    "Brand", all_brands, default=all_brands[:10] if len(all_brands) >= 10 else all_brands
)

price_min, price_max = float(df_full["price"].min()), float(df_full["price"].max())
price_range = st.sidebar.slider(
    "Price range (£)", price_min, price_max, (price_min, price_max), step=1.0
)

# Apply filters
df = df_full[
    df_full["Brand"].isin(selected_brands)
    & df_full["price"].between(*price_range)
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🛍️ ASOS Inventory Analytics Dashboard")
st.caption("Stockout-driven revenue loss across fashion products")

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Products", f"{len(df):,}")
k2.metric("Brands", f"{df['Brand'].nunique()}")
k3.metric("Avg Stockout Rate", f"{df['Stockout_Rate'].mean()*100:.1f}%")
k4.metric("Est. Lost Revenue", f"£{df['Lost_Revenue'].sum():,.0f}")

st.divider()

# ── Row 1 : Brand Strategy Scatter + Lost Revenue Bar ────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Brand Strategy Map")
    brand_agg = (
        df.groupby("Brand")
        .agg(Avg_Price=("price", "mean"), Stockout_Rate=("Stockout_Rate", "mean"),
             Lost_Revenue=("Lost_Revenue", "sum"), Products=("name", "count"))
        .reset_index()
    )
    brand_agg = brand_agg[brand_agg["Products"] > 10]
    fig1 = px.scatter(
        brand_agg, x="Avg_Price", y="Stockout_Rate",
        size="Lost_Revenue", color="Lost_Revenue",
        text="Brand", hover_data={"Products": True, "Lost_Revenue": ":,.0f"},
        color_continuous_scale="Viridis",
        labels={"Avg_Price": "Average Price (£)", "Stockout_Rate": "Stockout Rate",
                "Lost_Revenue": "Lost Revenue (£)"},
    )
    fig1.add_vline(x=40, line_dash="dash", line_color="red", annotation_text="£40")
    fig1.add_hline(y=0.4, line_dash="dash", line_color="red", annotation_text="40% OOS")
    fig1.update_traces(textposition="top center")
    fig1.update_layout(height=450, margin=dict(t=30))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Top 10 Brands by Lost Revenue")
    top_brands = brand_agg.nlargest(10, "Lost_Revenue")
    fig2 = px.bar(
        top_brands.sort_values("Lost_Revenue"),
        x="Lost_Revenue", y="Brand", orientation="h",
        color="Lost_Revenue", color_continuous_scale="Reds",
        labels={"Lost_Revenue": "Lost Revenue (£)", "Brand": ""},
    )
    fig2.update_layout(height=450, margin=dict(t=30), coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2 : Stockout distribution + Price vs Stockout heatmap ────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Stockout Rate Distribution by Brand")
    top15 = (
        df.groupby("Brand")["Lost_Revenue"].sum()
        .nlargest(15).index.tolist()
    )
    df_top15 = df[df["Brand"].isin(top15)]
    fig3 = px.box(
        df_top15, x="Brand", y="Stockout_Rate",
        color="Brand", points=False,
        labels={"Stockout_Rate": "Stockout Rate", "Brand": ""},
    )
    fig3.update_layout(height=400, showlegend=False,
                       xaxis_tickangle=-35, margin=dict(t=30))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Price Tier vs Stockout Rate")
    df["Price_Tier"] = pd.cut(
        df["price"],
        bins=[0, 20, 40, 60, 100, 9999],
        labels=["< £20", "£20–40", "£40–60", "£60–100", "£100+"],
    )
    heat_data = (
        df.groupby(["Brand", "Price_Tier"], observed=True)["Stockout_Rate"]
        .mean()
        .unstack("Price_Tier")
        .fillna(0)
    )
    heat_data = heat_data.loc[
        heat_data.sum(axis=1).nlargest(12).index
    ]
    fig4 = px.imshow(
        heat_data,
        color_continuous_scale="YlOrRd",
        labels=dict(color="Avg Stockout Rate"),
        aspect="auto",
    )
    fig4.update_layout(height=400, margin=dict(t=30))
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3 : Top products table ────────────────────────────────────────────────
st.subheader("🏴‍☠️ Top Products Losing Revenue to Stockouts")
top_n = st.slider("Show top N products", 5, 50, 20)
cols_show = ["Brand", "name", "price", "Stockout_Count", "Stockout_Rate", "Lost_Revenue"]
top_products = (
    df.sort_values("Lost_Revenue", ascending=False)
    .head(top_n)[cols_show]
    .rename(columns={
        "name": "Product", "price": "Price (£)",
        "Stockout_Count": "Sizes OOS", "Stockout_Rate": "OOS Rate",
        "Lost_Revenue": "Lost Revenue (£)"
    })
)
top_products["Price (£)"] = top_products["Price (£)"].map("£{:.2f}".format)
top_products["OOS Rate"] = top_products["OOS Rate"].map("{:.0%}".format)
top_products["Lost Revenue (£)"] = top_products["Lost Revenue (£)"].map("£{:,.0f}".format)
st.dataframe(top_products, use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Built with Python · Pandas · Plotly · Streamlit")