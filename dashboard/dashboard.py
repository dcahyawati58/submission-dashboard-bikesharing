import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style="whitegrid")

# ======================
# LOAD DATA
# ======================
day_df = pd.read_csv("data_day.csv", parse_dates=["dteday"])

st.title("Dashboard Analisis Penyewaan Sepeda 🚲")

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.subheader("Filter Rentang Waktu")

    min_date = day_df["dteday"].min().date()
    max_date = day_df["dteday"].max().date()

    start_date, end_date = st.date_input(
        label="Pilih Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# ======================
# FILTER DATA
# ======================
filtered_df = day_df[
    (day_df["dteday"].dt.date >= start_date) &
    (day_df["dteday"].dt.date <= end_date)
]

# ======================
# VALIDASI
# ======================
if filtered_df.empty:
    st.warning("Data tidak tersedia untuk rentang tanggal tersebut.")
else:

    if st.checkbox("Tampilkan Data"):
        st.write(filtered_df.head())

    # ======================
    # MAPPING
    # ======================
    weather_map = {
        1: 'Clear',
        2: 'Mist/Cloudy',
        3: 'Light Rain/Snow',
        4: 'Heavy Rain/Snow'
    }

    season_map = {
        1: 'Spring',
        2: 'Summer',
        3: 'Fall',
        4: 'Winter'
    }

    filtered_df['weather_label'] = filtered_df['weather_situation'].map(weather_map)
    filtered_df['season_label'] = filtered_df['season'].map(season_map)
    filtered_df['day_type'] = filtered_df['workingday'].map({0: 'Weekend', 1: 'Working Day'})

    # ======================
    # CLUSTERING
    # ======================
    def categorize_rentals(x):
        if x <= 3000:
            return 'Rendah'
        elif 3001 <= x <= 5000:
            return 'Sedang'
        else:
            return 'Tinggi'

    filtered_df['Kategori_Penyewaan'] = filtered_df['total_rentals'].apply(categorize_rentals)

    # ======================
    # TABS
    # ======================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📈 Tren Waktu",
    "🌦️ Cuaca & Musim",
    "👥 Pengguna",
    "🔬 EDA Lanjutan"
    ])

    # ======================
    # TAB 1: OVERVIEW
    # ======================
    with tab1:
        st.subheader("Distribusi Kategori Penyewaan")

        fig, ax = plt.subplots(figsize=(8,5))
        sns.countplot(
            data=filtered_df,
            x='Kategori_Penyewaan',
            order=['Rendah','Sedang','Tinggi'],
            palette=['#D3D3D3','#D3D3D3','#1F77B4'],
            ax=ax
        )
        ax.set_xlabel("Kategori")
        ax.set_ylabel("Jumlah Hari")
        st.pyplot(fig)

        st.subheader("Distribusi Total Penyewaan Sepeda")

        fig, ax = plt.subplots(figsize=(8,5))
        sns.histplot(filtered_df['total_rentals'], kde=True, ax=ax)
        st.pyplot(fig)

        # Korelasi
        st.subheader("Korelasi Variabel")

        corr = filtered_df[['total_rentals','temp','atemp','humidity','wind_speed']].corr()

        fig, ax = plt.subplots(figsize=(8,5))
        sns.heatmap(corr, annot=True, cmap="Blues", fmt=".2f", ax=ax)
        st.pyplot(fig)

    # ======================
    # TAB 2: TREND BULAN
    # ======================
    with tab2:
        st.subheader("Tren Penyewaan Sepeda per Bulan")

        monthly_avg = filtered_df.groupby("month")["total_rentals"].mean().reset_index()

        max_val = monthly_avg["total_rentals"].max()
        max_month = monthly_avg.loc[monthly_avg["total_rentals"].idxmax(), "month"]

        fig, ax = plt.subplots(figsize=(10,5))

        sns.lineplot(
            data=monthly_avg,
            x='month',
            y='total_rentals',
            marker='o',
            color='gray',
            linewidth=2,
            ax=ax
        )

        ax.scatter(max_month, max_val, color='red', s=100, zorder=5, label='Tertinggi')

        ax.set_xlabel("Bulan")
        ax.set_ylabel("Rata-rata Penyewaan")
        ax.set_xticks(range(1,13))
        ax.legend()

        st.pyplot(fig)

    # ======================
    # TAB 3: CUACA & MUSIM
    # ======================
    with tab3:
        st.subheader("Pengaruh Cuaca")

        weather_avg = filtered_df.groupby("weather_label")["total_rentals"].mean().reset_index()
        weather_avg = weather_avg.sort_values(by="total_rentals", ascending=False)

        max_val = weather_avg["total_rentals"].max()
        colors = ['#1F77B4' if v == max_val else '#D3D3D3' for v in weather_avg["total_rentals"]]

        fig, ax = plt.subplots(figsize=(9,5))
        sns.barplot(x="weather_label", y="total_rentals", data=weather_avg, palette=colors, ax=ax)
        st.pyplot(fig)

        st.subheader("Pengaruh Musim")

        season_avg = filtered_df.groupby("season_label")["total_rentals"].mean().reset_index()
        season_avg = season_avg.sort_values(by="total_rentals", ascending=False)

        max_val = season_avg["total_rentals"].max()
        colors = ['#1F77B4' if v == max_val else '#D3D3D3' for v in season_avg["total_rentals"]]

        fig, ax = plt.subplots(figsize=(9,5))
        sns.barplot(x="season_label", y="total_rentals", data=season_avg, palette=colors, ax=ax)
        st.pyplot(fig)

    # ======================
    # TAB 4: Pengguna
    # ======================
    with tab4:
        st.subheader("Perbandingan Pengguna")

        user_group = filtered_df.groupby("day_type")[['casual','registered']].mean().reset_index()
        user_melt = user_group.melt(id_vars='day_type', var_name='User Type', value_name='Jumlah')

        fig, ax = plt.subplots(figsize=(9,5))
        sns.barplot(
            data=user_melt,
            x='day_type',
            y='Jumlah',
            hue='User Type',
            palette=['#1F77B4','#A9A9A9'],
            ax=ax
        )
        st.pyplot(fig)

        st.subheader("Kategori vs Cuaca")

        fig, ax = plt.subplots(figsize=(9,5))
        sns.countplot(
            data=filtered_df,
            x='Kategori_Penyewaan',
            hue='weather_label',
            order=['Rendah','Sedang','Tinggi'],
            palette={
                'Clear': '#1F77B4',
                'Mist/Cloudy': '#D3D3D3',
                'Light Rain/Snow': '#A9A9A9',
                'Heavy Rain/Snow': '#808080'
            },
            ax=ax
        )
        st.pyplot(fig)
        
    # ======================
    # TAB 5: EDA Lanjutan
    # ======================
    with tab5:

        subtab1, subtab2, subtab3, subtab4 = st.tabs([
            "Distribusi",
            "Hubungan",
            "Normalitas",
            "Kategori"
        ])
        
        with subtab1:
            st.subheader("Distribusi Variabel Numerik")

            num_cols = ['temp','atemp','humidity','wind_speed','total_rentals']

            fig, axes = plt.subplots(3,2, figsize=(12,10))
            axes = axes.flatten()

            for i, col in enumerate(num_cols):
                sns.histplot(filtered_df[col], kde=True, ax=axes[i])
                axes[i].set_title(f'Distribusi {col}')

            plt.tight_layout()
            st.pyplot(fig)
        
        with subtab2:
            st.subheader("Heatmap Korelasi")

            corr = filtered_df[['temp','atemp','humidity','wind_speed','casual','registered','total_rentals']].corr()

            fig, ax = plt.subplots(figsize=(8,5))
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
            st.pyplot(fig)

            st.subheader("Scatter Plot")

            fig, ax = plt.subplots(figsize=(8,5))
            sns.scatterplot(data=filtered_df, x='temp', y='total_rentals', ax=ax)
            st.pyplot(fig)

            fig, ax = plt.subplots(figsize=(8,5))
            sns.scatterplot(data=filtered_df, x='humidity', y='total_rentals', ax=ax)
            st.pyplot(fig)
            
        with subtab3:
            import scipy.stats as stats

            st.subheader("Q-Q Plot Total Rentals")

            fig, ax = plt.subplots(figsize=(6,6))
            stats.probplot(filtered_df['total_rentals'], dist="norm", plot=ax)
            st.pyplot(fig)

            st.subheader("Shapiro-Wilk Test")

            from scipy.stats import shapiro
            stat, p = shapiro(filtered_df['total_rentals'].sample(500))

            st.write(f"Statistic: {stat}")
            st.write(f"p-value: {p}")
            
        with subtab4:
            st.subheader("Distribusi Penyewaan Berdasarkan Musim")

            fig, ax = plt.subplots(figsize=(8,5))
            sns.violinplot(x='season_label', y='total_rentals', data=filtered_df, ax=ax)
            st.pyplot(fig)

            st.subheader("Distribusi Penyewaan Berdasarkan Cuaca")

            fig, ax = plt.subplots(figsize=(8,5))
            sns.violinplot(x='weather_label', y='total_rentals', data=filtered_df, ax=ax)
            st.pyplot(fig)
