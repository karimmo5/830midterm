import streamlit as st
import pandas as pd
import plotly.express as px

# INITIAL DATA PROCESSING AND CLEANING

pc_data = pd.read_csv("logicalincrements_history_2013_to_2024.csv", header = None)

# Column names
pc_data.columns = [
    "Date",
    "Tier",
    "Graphics",
    "CPU",
    "Motherboard",
    "RAM",
    "Total"
]

# Preparing for Removal of FAILED rows
pc_data = pc_data[
    pc_data["Tier"] != "FAILED +/- 1 MONTH" # Removes failed observations
]
    
# Delete rows where all cells are missing (empty rows)
pc_data = pc_data.dropna(how = "all") # how = "all" checks if all cells are missing, i.e. empty rows

# Convert date observations to readable dates
pc_data["Date"] = pd.to_datetime( # method to convert the date observations in the form of YYYYMMDD to something usable and comparable
    pc_data["Date"],
    format="%Y%m%d",
)

# Forward fill (allows us to propagate date observations)
pc_data["Date"] = pc_data["Date"].ffill()

# Remove extra header rows and only leave observations
pc_data = pc_data[pc_data["Tier"] != "Tier"]

# Convert Total column to integer (requires removal of $ symbol and whitespace) and RAM column to integer (need to remove $ symbol and the numbers after)
pc_data["Total"] = (
    pc_data["Total"]
    .astype("string") # converts to string
    .str.replace(",", "", regex=False) # replaces commas with nothing. need to specify regex=False for this and next call since Python defaults to True
    .str.strip() # removes whitespace
    .str.replace("$", "", regex=False) # replaces $ with nothing
)

pc_data["Total"] = pd.to_numeric(pc_data["Total"]).astype(int) # Method to convert total prices to integers

# Convert all other columns to strings (intermediary step for RAM, we still need to remove the GB from the entries

pc_data["Tier"] = pc_data["Tier"].str.strip().str.capitalize() # Turns out there are both "Very good" and "Very Good" tiers, which are not meant to be distinct
pc_data["Tier"] = pc_data["Tier"].astype("string")
pc_data["Graphics"] = pc_data["Graphics"].astype("string")
pc_data["CPU"] = pc_data["CPU"].astype("string")
pc_data["Motherboard"] = pc_data["Motherboard"].astype("string")
pc_data["RAM"] = pc_data["RAM"].astype("string")

# Extract part price and insert into separate column

cols = ["Graphics", "CPU", "Motherboard", "RAM"]

for col in cols:
    extracted = pc_data[col].str.extract(r'\$\s*(\S+)\s*$')[0] # Extracts the $XX from the part columns
    
    pc_data[col] = pc_data[col].str.replace(r'\s*\$\s*\S+\s*$', '', regex = True).str.strip() # Removes the $XX from the original part columns
    
    index = pc_data.columns.get_loc(col) + 1 # Numerical index of current column + 1 to insert price column
    
    pc_data.insert(index, f"{col}_Price", extracted) # Inserts part price column directly after part column
    
    pc_data[f"{col}_Price"] = pd.to_numeric(pc_data[f"{col}_Price"]).astype(int) # Converts prices to integers
    
# Remove GB label from the RAM columns

pc_data["RAM"] = (
    pd.to_numeric(
        pc_data["RAM"]
        .str.replace(r"\s*GB.*", "", regex = True)
    )
    .astype(int)
)

# Reset indices for ease of access

pc_data = pc_data.reset_index(drop=True)

# STREAMLIT IMPLEMENTATION

st.set_page_config(
    page_title="PC Build Price Analysis",
    layout="wide"
)

st.title("PC Build Price Analysis")
tiers_list = sorted(pc_data["Tier"].dropna().unique().tolist())
available_years = pc_data["Date"].dropna().dt.year

# Scatterplot stuff
st.subheader("Price Over Time by Tier")

selected_tiers = st.multiselect(
    "Select tiers for price-over-time plot",
    options=tiers_list,
    default=tiers_list,
    key="line_tiers"
)

filtered_data = pc_data[pc_data["Tier"].isin(selected_tiers)].copy()

if not filtered_data.empty:
    fig = px.line(
        filtered_data,
        x="Date",
        y="Total",
        color="Tier",
        markers=True,
        hover_data={
            col: True
            for col in filtered_data.columns
            if col != "Total"
        },
        labels={
            "Date": "Date",
            "Total": "Build Price (2024 USD)",
            "Tier": "Tier of Build"
        },
        title="Price Over Time by Tier"
    )

    fig.update_layout(
        autosize=True,
        height=500,
        margin=dict(l=40, r=30, t=70, b=50)
    )

    st.plotly_chart(fig, width="stretch")
else:
    st.info("No data available for the selected tiers.")

# Histogram
st.subheader("Distribution of Build Prices")

if not available_years.empty:
    min_year = int(available_years.min())
    max_year = int(available_years.max())

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        start_year = st.number_input(
            "Starting year",
            min_value=min_year,
            max_value=max_year,
            value=min_year,
            step=1,
            key="hist_start_year"
        )

    with col2:
        end_year = st.number_input(
            "Ending year",
            min_value=min_year,
            max_value=max_year,
            value=max_year,
            step=1,
            key="hist_end_year"
        )

    with col3:
        histogram_tiers = st.multiselect(
            "Select tiers for histogram",
            options=tiers_list,
            default=tiers_list,
            key="hist_tiers"
        )

    if start_year > end_year:
        st.warning(
            "The starting year must be less than "
            "or equal to the ending year."
        )
    else:
        histogram_data = pc_data[
            (pc_data["Date"].dt.year >= start_year)
            & (pc_data["Date"].dt.year <= end_year)
            & (pc_data["Tier"].isin(histogram_tiers))
        ].copy()

        histogram_data = histogram_data.dropna(
            subset=["Date", "Total"]
        )

        if not histogram_data.empty:
            mean_price = histogram_data["Total"].mean()
            median_price = histogram_data["Total"].median()

            chart_col, stats_col = st.columns([4, 1])

            with chart_col:
                hist_fig = px.histogram(
                    histogram_data,
                    x="Total",
                    color="Tier",
                    nbins=30,
                    barmode="stack",
                    labels={
                        "Total": "Build Price (2024 USD)",
                        "count": "Number of Builds",
                        "Tier": "Tier of Build"
                    },
                    title=(
                        f"Build Price Distribution "
                        f"({start_year}–{end_year})"
                    ),
                    hover_data={
                        "Tier": True,
                        "Total": False
                    }
                )

                hist_fig.add_vline(
                    x=mean_price,
                    line_dash="dot",
                    line_color="orange",
                    line_width=3,
                    annotation_text="Mean",
                    annotation_position="top"
                )

                hist_fig.add_vline(
                    x=median_price,
                    line_dash="dot",
                    line_color="green",
                    line_width=3,
                    annotation_text="Median",
                    annotation_position="top"
                )

                hist_fig.update_layout(
                    autosize=True,
                    height=500,
                    margin=dict(l=40, r=30, t=90, b=50),
                    xaxis_title="Build Price (2024 USD)",
                    yaxis_title="Number of Builds",
                    bargap=0.05
                )

                st.plotly_chart(
                    hist_fig,
                    width="stretch"
                )

            with stats_col:
                st.markdown("### Statistics")

                st.markdown(
                    "<span style='color:orange; font-weight:bold;'>"
                    "Mean</span>",
                    unsafe_allow_html=True
                )
                st.metric(
                    label="Mean build price",
                    value=f"${mean_price:,.2f}"
                )

                st.markdown(
                    "<span style='color:green; font-weight:bold;'>"
                    "Median</span>",
                    unsafe_allow_html=True
                )
                st.metric(
                    label="Median build price",
                    value=f"${median_price:,.2f}"
                )

                st.divider()

                st.metric(
                    label="Total builds",
                    value=f"{len(histogram_data):,}"
                )

                st.metric(
                    label="Tiers represented",
                    value=histogram_data["Tier"].nunique()
                )

            st.caption(
                f"Showing {len(histogram_data)} build records "
                f"across {histogram_data['Tier'].nunique()} tiers, "
                f"from {start_year} through {end_year}, inclusive."
            )

            with st.expander("Inspect builds included in histogram"):
                st.dataframe(
                    histogram_data[
                        ["Date", "Tier", "Total"]
                    ].sort_values(["Date", "Tier"]),
                    width="stretch"
                )

                st.write("Records per tier and year:")

                counts = (
                    histogram_data.assign(
                        Year=histogram_data["Date"].dt.year
                    )
                    .groupby(["Year", "Tier"])
                    .size()
                    .reset_index(name="Build Count")
                    .sort_values(["Year", "Tier"])
                )

                st.dataframe(
                    counts,
                    width="stretch"
                )

        else:
            st.info(
                "No build prices found for the selected "
                "tiers and year range."
            )
else:
    st.warning("No valid dates were found in the dataset.")