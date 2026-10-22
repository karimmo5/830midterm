# About

This project was created to streamline the research process for historical price data of consumer-grade desktop PCs at a glance. It features PC builds across 10 different price tiers and their total prices. While usable by anyone, the intended audience is for those who want to know how build prices have shifted over the years, such as computer scientists doing preliminary research or newbie PC builders who aren't sure where to start in terms of budget.

# Setup

This program is created using Python 3.14. A similar interpreter must be used to run the application.

1. Download the project's ZIP file and extract to a desired location
2. Ensure the requirements to run the application are met, which are the following packages:
	- `pandas`
	- `numpy`
	- `plotly`
	- `streamlit`

If packages are missing, run the following command in the same directory as the downloaded requirements.txt file:
`python -m pip install -r requirements.txt`

3. After ensuring `logicalincrements_history_2013_to_2024.csv` and `app.py` are downloaded and present in the same folder, run the following command in the directory containing both files:
streamlit run app.py

# Dataset used

The dataset used was collected by Ryan A. Gibson and his team [source](https://ryanagibson.com/extra/historical-pc-build-data/). This data was collected using the help of Internet Archive from Logical Increments, a guide website for PC building. There are several columns within the dataset initially:

- Date, which contains the date of observation (spans from end of 2012 to middle of 2024 despite the file name, with three months between observations)
- Tier, which is the tier of PC build ranging from "minimal" to "extremist" (see limitations for details)
- Graphics, which contains the graphics card used in the specific build as well as the part's individual price.
- CPU, which contains the CPU used in the specific build as well as the part's individual price.
- Motherboard, which contains the motherboard used in the specific build as well as the part's individual price.
- RAM, which contains the RAM used in the specific build as well as the part's individual price.
- Total, the total price of the build. Includes other, more minor parts that were not very necessary or impactful on the price, such as power supply.

A few other columns will be added upon running the application, all of which are of the form (PARTNAME_Price). The data will be adjusted in Python to have the name and price columns separated for ease of reference. Prices are recorded in 2024 USD.

# Limitations

The biggest issue facing this project is a lack of a clear definition of what the tiers represent. While they are intended to represent different price categories, I could not find the definition of these tiers on either Gibson's website or Logical Increments's website. A lack of benchmark and performance numbers also hinders creating these definitions ourselves, and as such all that can be done is to look at the data as initial/introductory research. This is the best solution for the user, as it is unclear what user would call what price/performance range what tier.

# How to Use

This application features two plots: a scatterplot and a histogram.

- The scatterplot represents the historical price trends for the ten different tiers. You can mouse over an observation for the details for that particular build. There also exists a filtering system that allows you to select the tiers you wish to view, if you are only looking for data on particular tiers.

- The histogram represents the distribution of build prices, as well as a line representing the mean and median of the selected distribution. Similar to the scatterplot, you can select what tiers you wish to view data for. You can also select the years to view the data for, specifying an inclusive range that will calculate the distribution only builds within the range given that also meet the tier filter. Mousing over bins will show both the total count of builds within a given bin as well as its composition (i.e. how many counts of the different tiers are in said bin).