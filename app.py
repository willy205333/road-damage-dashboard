import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


st.set_page_config(
    page_title="Road Surface Tracking System",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css():
    st.markdown("""
    <style>
        .main {
            background-color: #f5f7f9;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            margin: 0;
            height: auto;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #4e8df5;
            color: white;
        }
        .stButton>button {
            background-color: #4e8df5;
            color: white;
            border-radius: 6px;
            padding: 0.5em 1em;
            font-weight: 500;
        }
        .css-1v3fvcr {
            background-color: #f5f7f9;
        }
        h1, h2, h3 {
            color: #1e3a8a;
        }
        .section-title {
            background-color: #e3f2fd;
            padding: 10px !important;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .sized-box {
            height: 30px;
        }
    </style>
    """, unsafe_allow_html=True)

def load_data(file_path='dummy_data_yogyakarta.csv'):
    """Load data dari file CSV"""
    try:
        data = pd.read_csv(file_path)
        return data
    except FileNotFoundError:
        st.error(f"File {file_path} tidak ditemukan. Pastikan file CSV tersedia di direktori yang benar.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
        return None

def sidebar():
    """Fungsi untuk membuat sidebar"""
    with st.sidebar:
        st.title("Road Surface Tracking System")
        
        st.markdown("---")
        st.subheader("Filter Data")
        
        kondisi_options = ['Semua', 'Sangat Baik', 'Baik', 'Sedang', 'Buruk']
        kondisi_filter = st.multiselect("Kondisi Jalan:", kondisi_options, default='Semua')
        
        st.subheader("Filter IRI (m/km)")
        min_iri, max_iri = st.slider("Range IRI:", 0.0, 10.0, (0.0, 10.0), 0.1)
        
        st.markdown("---")
        
        st.markdown("### Tentang Aplikasi")
        st.info("""
        Road Surface Tracking System adalah website untuk monitoring dan analisis kerataan permukaan jalan. 
        Data dikumpulkan menggunakan perangkat khusus yang mengukur beberapa parameter kualitas jalan.
        """)
        
        if st.button("Bantuan"):
            st.info("""
            **Cara Penggunaan:**
            1. Unggah data CSV atau gunakan data sampel
            2. Gunakan filter untuk menyaring data
            3. Gunakan tab di halaman utama untuk melihat visualisasi yang berbeda
            """)
    
    return kondisi_filter, min_iri, max_iri

def filter_data(data, kondisi_filter, min_iri, max_iri):
    """Filter data berdasarkan kondisi dan IRI"""
    filtered_data = data.copy()
    
    if 'Semua' not in kondisi_filter and kondisi_filter:
        filtered_data = filtered_data[filtered_data['Roughness Condition'].isin(kondisi_filter)]
    
    filtered_data = filtered_data[(filtered_data['IRI (m/km)'] >= min_iri) & (filtered_data['IRI (m/km)'] <= max_iri)]
    
    return filtered_data

def create_map(data):
    """Membuat peta dengan marker untuk setiap segmen jalan"""
    m = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=14)
    
    color_dict = {
        'Sangat Baik': 'green',
        'Baik': 'blue',
        'Sedang': 'orange',
        'Buruk': 'red'
    }
    
    for idx, row in data.iterrows():
        tooltip_text = f"""
        <strong>Segmen:</strong> {row['Start Point (m)']} - {row['End Point (m)']} m<br>
        <strong>IRI:</strong> {row['IRI (m/km)']} m/km<br>
        <strong>Kondisi:</strong> {row['Roughness Condition']}<br>
        <strong>Retak:</strong> {row['Total Crack Area (%)']}%<br>
        <strong>Lubang:</strong> {row['Number of Potholes (per km)']} per km
        """
        
        color = color_dict.get(row['Roughness Condition'], 'gray')
        
        folium.Circle(
            location=[row['Latitude'], row['Longitude']],
            radius=50,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            tooltip=folium.Tooltip(tooltip_text)
        ).add_to(m)
    
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; z-index:9999; background-color:white; 
                padding: 10px; border-radius: 5px; border: 2px solid grey; width: 180px;">
        <p><strong>Kondisi Jalan:</strong></p>
        <p><i class="fa fa-circle" style="color:green"></i> Sangat Baik</p>
        <p><i class="fa fa-circle" style="color:blue"></i> Baik</p>
        <p><i class="fa fa-circle" style="color:orange"></i> Sedang</p>
        <p><i class="fa fa-circle" style="color:red"></i> Buruk</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def dashboard_overview(data):
    """Menampilkan dashboard overview"""
    st.markdown("<h2 class='section-title'>Dashboard Monitoring Jalan</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.metric("Panjang Jalan Total", f"{(data['End Point (m)'].max() - data['Start Point (m)'].min()) / 1000:.2f} km")

    
    with col2:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.metric("IRI Rata-rata", f"{data['IRI (m/km)'].mean():.2f} m/km")

    
    with col3:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.metric("Retak Rata-rata", f"{data['Total Crack Area (%)'].mean():.2f}%")

    
    with col4:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.metric("Lubang Rata-rata", f"{data['Number of Potholes (per km)'].mean():.1f} per km")

    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Distribusi Kondisi Jalan")
        kondisi_count = data['Roughness Condition'].value_counts().reset_index()
        kondisi_count.columns = ['Kondisi', 'Jumlah']
        
        colors = {'Sangat Baik': '#2ecc71', 'Baik': '#3498db', 'Sedang': '#f39c12', 'Buruk': '#e74c3c'}
        fig = px.pie(kondisi_count, values='Jumlah', names='Kondisi', 
                     color='Kondisi', color_discrete_map=colors,
                     hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    
    with col2:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Distribusi IRI (m/km)")
        fig = px.histogram(data, x='IRI (m/km)', nbins=20, 
                          color_discrete_sequence=['#4e8df5'])
        fig.add_vline(x=data['IRI (m/km)'].mean(), line_dash="dash", line_color="red",
                     annotation_text=f"Rata-rata: {data['IRI (m/km)'].mean():.2f}")
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    
    st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
    st.subheader("Peta Kondisi Jalan")
    map_obj = create_map(data)
    folium_static(map_obj, width=1200, height=500)
    st.markdown("</div>", unsafe_allow_html=True)

def crack_analysis(data):
    """Analisis detail retak"""
    st.markdown("<h2 class='section-title'>Analisis Retak Jalan</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Area Retak sepanjang Segmen Jalan")
        fig = px.line(data, x='Start Point (m)', y='Total Crack Area (%)', 
                      markers=True, line_shape='linear',
                      color_discrete_sequence=['#f39c12'])
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    
    with col2:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Distribusi Lebar Retak")
        fig = px.histogram(data, x='Average Crack Width (mm)', nbins=15,
                           color_discrete_sequence=['#f39c12'])
        fig.add_vline(x=data['Average Crack Width (mm)'].mean(), line_dash="dash", line_color="red",
                     annotation_text=f"Rata-rata: {data['Average Crack Width (mm)'].mean():.2f} mm")
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Hubungan Area Retak dan Lebar Retak")
        fig = px.scatter(data, x='Total Crack Area (%)', y='Average Crack Width (mm)', 
                         color='Roughness Condition', size='IRI (m/km)',
                         color_discrete_map={'Sangat Baik': '#2ecc71', 'Baik': '#3498db', 
                                           'Sedang': '#f39c12', 'Buruk': '#e74c3c'})
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    
    with col2:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Area Retak berdasarkan Kondisi Jalan")
        fig = px.box(data, x='Roughness Condition', y='Total Crack Area (%)', 
                     color='Roughness Condition',
                     color_discrete_map={'Sangat Baik': '#2ecc71', 'Baik': '#3498db', 
                                       'Sedang': '#f39c12', 'Buruk': '#e74c3c'})
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)


def pothole_analysis(data):
    """Analisis detail lubang"""
    st.markdown("<h2 class='section-title'>Analisis Lubang Jalan</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Jumlah Lubang sepanjang Segmen Jalan")
        fig = px.bar(data, x='Start Point (m)', y='Number of Potholes (per km)',
                     color='Roughness Condition',
                     color_discrete_map={'Sangat Baik': '#2ecc71', 'Baik': '#3498db', 
                                       'Sedang': '#f39c12', 'Buruk': '#e74c3c'})
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    
    with col2:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Distribusi Jumlah Lubang")
        fig = px.histogram(data, x='Number of Potholes (per km)', nbins=15,
                           color_discrete_sequence=['#e74c3c'])
        fig.add_vline(x=data['Number of Potholes (per km)'].mean(), line_dash="dash", line_color="red",
                     annotation_text=f"Rata-rata: {data['Number of Potholes (per km)'].mean():.2f} per km")
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Jumlah Lubang berdasarkan Kondisi Jalan")
        fig = px.box(data, x='Roughness Condition', y='Number of Potholes (per km)', 
                     color='Roughness Condition',
                     color_discrete_map={'Sangat Baik': '#2ecc71', 'Baik': '#3498db', 
                                       'Sedang': '#f39c12', 'Buruk': '#e74c3c'})
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    
    with col2:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Hubungan IRI dengan Jumlah Lubang")
        fig = px.scatter(data, x='IRI (m/km)', y='Number of Potholes (per km)', 
                         color='Roughness Condition', size='Total Crack Area (%)',
                         color_discrete_map={'Sangat Baik': '#2ecc71', 'Baik': '#3498db', 
                                           'Sedang': '#f39c12', 'Buruk': '#e74c3c'},
                         trendline="ols")
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)


def rut_analysis(data):
    """Analisis detail alur roda (rutting)"""
    st.markdown("<h2 class='section-title'>Analisis Alur Roda (Rutting)</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Kedalaman Alur sepanjang Segmen Jalan")
        fig = px.line(data, x='Start Point (m)', y='Average Rut Depth (cm)', 
                      markers=True, line_shape='linear',
                      color_discrete_sequence=['#8e44ad'])
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    
    with col2:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Distribusi Kedalaman Alur")
        fig = px.histogram(data, x='Average Rut Depth (cm)', nbins=15,
                           color_discrete_sequence=['#8e44ad'])
        fig.add_vline(x=data['Average Rut Depth (cm)'].mean(), line_dash="dash", line_color="red",
                     annotation_text=f"Rata-rata: {data['Average Rut Depth (cm)'].mean():.2f} cm")
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Kedalaman Alur berdasarkan Kondisi Jalan")
        fig = px.box(data, x='Roughness Condition', y='Average Rut Depth (cm)', 
                     color='Roughness Condition',
                     color_discrete_map={'Sangat Baik': '#2ecc71', 'Baik': '#3498db', 
                                       'Sedang': '#f39c12', 'Buruk': '#e74c3c'})
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    
    with col2:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        st.subheader("Hubungan IRI dengan Kedalaman Alur")
        fig = px.scatter(data, x='IRI (m/km)', y='Average Rut Depth (cm)', 
                         color='Roughness Condition', size='Speed (km/h)',
                         color_discrete_map={'Sangat Baik': '#2ecc71', 'Baik': '#3498db', 
                                           'Sedang': '#f39c12', 'Buruk': '#e74c3c'},
                         trendline="ols")
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)


def report_tab(data):
    """Tab untuk laporan"""
    st.markdown("<h2 class='section-title'>Laporan Kondisi Jalan</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
    st.header("Rangkuman Kondisi Jalan")
    
    kondisi_count = data['Roughness Condition'].value_counts()
    persentase = (kondisi_count / len(data) * 100).round(2)
    
    st.markdown(f"""
    ### Distribusi Kondisi Jalan
    
    - **Sangat Baik**: {persentase.get('Sangat Baik', 0)}% ({kondisi_count.get('Sangat Baik', 0)} segmen)
    - **Baik**: {persentase.get('Baik', 0)}% ({kondisi_count.get('Baik', 0)} segmen)
    - **Sedang**: {persentase.get('Sedang', 0)}% ({kondisi_count.get('Sedang', 0)} segmen)
    - **Buruk**: {persentase.get('Buruk', 0)}% ({kondisi_count.get('Buruk', 0)} segmen)
    
    ### Statistik Kerusakan
    
    - **Rata-rata IRI**: {data['IRI (m/km)'].mean():.2f} m/km (Minimum: {data['IRI (m/km)'].min():.2f}, Maksimum: {data['IRI (m/km)'].max():.2f})
    - **Rata-rata Area Retak**: {data['Total Crack Area (%)'].mean():.2f}% (Minimum: {data['Total Crack Area (%)'].min():.2f}%, Maksimum: {data['Total Crack Area (%)'].max():.2f}%)
    - **Rata-rata Jumlah Lubang**: {data['Number of Potholes (per km)'].mean():.2f} per km (Minimum: {data['Number of Potholes (per km)'].min():.2f}, Maksimum: {data['Number of Potholes (per km)'].max():.2f})
    - **Rata-rata Kedalaman Alur**: {data['Average Rut Depth (cm)'].mean():.2f} cm (Minimum: {data['Average Rut Depth (cm)'].min():.2f} cm, Maksimum: {data['Average Rut Depth (cm)'].max():.2f} cm)
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        fig = go.Figure()
        
        categories = ['IRI (m/km)', 'Total Crack Area (%)', 'Avg Crack Width (mm)', 
                     'Potholes (per km)', 'Rut Depth (cm)']
        
        for kondisi in ['Sangat Baik', 'Baik', 'Sedang', 'Buruk']:
            if kondisi in data['Roughness Condition'].unique():
                kondisi_data = data[data['Roughness Condition'] == kondisi]
                
                values = [
                    kondisi_data['IRI (m/km)'].mean(),
                    kondisi_data['Total Crack Area (%)'].mean(),
                    kondisi_data['Average Crack Width (mm)'].mean(),
                    kondisi_data['Number of Potholes (per km)'].mean(),
                    kondisi_data['Average Rut Depth (cm)'].mean()
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=kondisi
                ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([
                        data['IRI (m/km)'].max(),
                        data['Total Crack Area (%)'].max() / 3,
                        data['Average Crack Width (mm)'].max(),
                        data['Number of Potholes (per km)'].max() / 5,
                        data['Average Rut Depth (cm)'].max()
                    ])]
                )),
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)

    
    with col2:
        st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
        need_repair = data[data['IRI (m/km)'] > 8]
        repair_percent = len(need_repair) / len(data) * 100
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = repair_percent,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Segmen Memerlukan Perbaikan (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#e74c3c"},
                'steps': [
                    {'range': [0, 20], 'color': "#2ecc71"},
                    {'range': [20, 40], 'color': "#f1c40f"},
                    {'range': [40, 60], 'color': "#f39c12"},
                    {'range': [60, 100], 'color': "#e74c3c"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Segmen yang Perlu Diperbaiki")
        if len(need_repair) > 0:
            st.dataframe(need_repair[['Start Point (m)', 'End Point (m)', 'IRI (m/km)', 
                                     'Roughness Condition', 'Number of Potholes (per km)']])
        else:
            st.info("Tidak ada segmen yang memerlukan perbaikan mendesak.")

    
    st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
    st.subheader("Rekomendasi Perbaikan")
    
    high_priority = data[data['IRI (m/km)'] > 8]
    medium_priority = data[(data['IRI (m/km)'] > 5) & (data['IRI (m/km)'] <= 8)]
    low_priority = data[(data['IRI (m/km)'] > 3) & (data['IRI (m/km)'] <= 5)]
    
    high_panjang = (high_priority['End Point (m)'].max() - high_priority['Start Point (m)'].min()) if len(high_priority) > 0 else 0
    medium_panjang = (medium_priority['End Point (m)'].max() - medium_priority['Start Point (m)'].min()) if len(medium_priority) > 0 else 0
    low_panjang = (low_priority['End Point (m)'].max() - low_priority['Start Point (m)'].min()) if len(low_priority) > 0 else 0
    
    st.markdown(f"""
    ### Prioritas Perbaikan
    
    1. **Prioritas Tinggi** (IRI > 8 m/km):
       - Jumlah Segmen: {len(high_priority)}
       - Panjang Total: {high_panjang/1000:.2f} km
       - Tindakan: Rekonstruksi jalan atau overlay tebal
    
    2. **Prioritas Menengah** (5 < IRI ≤ 8 m/km):
       - Jumlah Segmen: {len(medium_priority)}
       - Panjang Total: {medium_panjang/1000:.2f} km
       - Tindakan: Overlay tipis atau penambalan lubang masif
    
    3. **Prioritas Rendah** (3 < IRI ≤ 5 m/km):
       - Jumlah Segmen: {len(low_priority)}
       - Panjang Total: {low_panjang/1000:.2f} km
       - Tindakan: Pemeliharaan rutin, penambalan lubang
    """)
    st.markdown("</div>", unsafe_allow_html=True)

def data_table(data):
    """Tab untuk menampilkan data dalam bentuk tabel"""
    st.markdown("<h2 class='section-title'>Data Kerataan Jalan</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='sized-box'></div>", unsafe_allow_html=True)
    csv = data.to_csv(index=False)
    st.download_button(
        label="Download Data CSV",
        data=csv,
        file_name="road_condition_data.csv",
        mime="text/csv",
    )
    
    st.dataframe(data, height=500)
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Fungsi utama aplikasi"""
    local_css()
    
    st.title("🛣️ Road Surface Tracking System")
    st.markdown("Aplikasi untuk monitoring dan analisis kerataan permukaan jalan")
    
    kondisi_filter, min_iri, max_iri = sidebar()
    
    data = load_data()
    
    if data is not None:
        filtered_data = filter_data(data, kondisi_filter, min_iri, max_iri)
        
        tabs = st.tabs(["Dashboard", "Analisis Retak", "Analisis Lubang", "Analisis Alur", "Laporan", "Data"])
        
        with tabs[0]:
            dashboard_overview(filtered_data)
        
        with tabs[1]:
            crack_analysis(filtered_data)
        
        with tabs[2]:
            pothole_analysis(filtered_data)
        
        with tabs[3]:
            rut_analysis(filtered_data)
        
        with tabs[4]:
            report_tab(filtered_data)
        
        with tabs[5]:
            data_table(filtered_data)
    else:
        st.error("Tidak dapat memuat data. Silakan periksa ketersediaan file CSV.")
        st.info("Untuk menjalankan aplikasi ini, pastikan file CSV tersedia di direktori yang benar.")

if __name__ == "__main__":
    main()
