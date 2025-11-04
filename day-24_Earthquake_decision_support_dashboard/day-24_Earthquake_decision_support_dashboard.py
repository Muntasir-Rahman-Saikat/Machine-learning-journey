from mailcap import subst

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime,timedelta
import warnings



warnings.filterwarnings('ignore')
st.set_page_config(
    page_title='Earthquake Decision Support Dashboard',
    layout='wide',
    initial_sidebar_state='expanded',
)
st.title('Earthquake Decision Support Dashboard')
st.markdown(
    "**Real-Time monitoring,clustering and decision suppoort for geologists"
)
uploaded_files=st.file_uploader(
   label="Upload Earthquake CSV files",
    type='csv'
)
def load_and_process_data(uploaded_files):
    df=pd.read_csv(uploaded_files)
    df['time']=pd.to_datetime(
        df['time'],
        format='%Y-%m-%d %H:%M:%S.%f',
        errors='coerce'
    )
    df=df.dropna(subset=['time'])
    df['date']=df['time'].dt.date
    df['year']=df['time'].dt.year
    df['month']=df['time'].dt.month
    df['hour']=df['time'].dt.hour
    df['day_of_week']=df['time'].dt.day_name()
    df['risk_level']=pd.cut(
        df['magnitude'],
        bins=[0,4.0,5.5,6.5,np.inf],
        labels=['low','Moderate','High','Critical']
    )
    df['tectonic_type']=np.where(
        df['depth']<70,'Crustal',#if depth less than 70 print Crustal
        np.where(
            df['depth']<300,"Intermediate","Deep"#else if depth less than 300 print Intermediate else Deep
        )
    )
    df=df.sort_values('time').reset_index(drop=True)
    df['hours_since_prev']=df['time'].diff().dt.total_seconds()/3600
    df['hours_since_prev']=df['hours_since_prev'].fillna(0)
    df['cluster_flag']=df['hours_since_prev']<24
    return df
if uploaded_files is not None:
    st.markdown("Uploaded file successfully")
    with st.spinner("Loading data..."):      #will kept showing loading until df is returned
        df=load_and_process_data(uploaded_files)

    # Apply filters
    st.sidebar.header("Filter")
    time_window = st.sidebar.selectbox(
        'Time Window',
        ['All time', 'Last 7 days', 'Last 30 days', 'Last 90 days', 'Custom']
    )
    if time_window == 'Custom':
        start_date = st.sidebar.date_input('start', df['date'].min())
        end_date = st.sidebar.date_input('End', df['date'].max())
        filter_df = df[(df['date'] > start_date) & (df['date'] < end_date)]
    else:
        days = {'All time': 99999, "Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
        cut_off = df['time'].max() - timedelta(days=days[time_window])
        filter_df = df[df['time'] >= cut_off]
    mag_range = st.sidebar.slider(
        label="Magnitude",
        min_value=float(df['magnitude'].min()),
        max_value=float(df['magnitude'].max()),
        value=(4.0, 7.0)
    )
    depth_range = st.sidebar.slider("Depth (km)",
                                    float(df['depth'].min()), float(df['depth'].max()),
                                    (float(df['depth'].min()), float(df['depth'].max())))
    risk_levels = st.sidebar.multiselect("Risk Level",
                                         ['Low', 'Moderate', 'High', 'Critical'],
                                         default=['Moderate', 'High', 'Critical'])
    tectonic_types = st.sidebar.multiselect("Tectonic Type",
                                            ['Crustal', 'Intermediate', 'Deep'],
                                            default=['Crustal', 'Intermediate', 'Deep'])

    filter_df = filter_df[
        (filter_df['magnitude'].between(mag_range[0], mag_range[1])) &
        (filter_df['depth'].between(depth_range[0], depth_range[1])) &
        (filter_df['risk_level'].isin(risk_levels)) &
        (filter_df['tectonic_type'].isin(tectonic_types))
        ]

    st.markdown("---")
    st.header("Executive header")
    col1,col2,col3,col4,col5=st.columns(5)
    total_events=len(filter_df)
    critical_events=len(filter_df[filter_df['risk_level']=='Critical'])
    last_24_hours=len(filter_df[(filter_df['time'] > (filter_df['time'].max()-timedelta(hours=24))) & (filter_df['time'] < (filter_df['time'].max()))])
    avg_mag=filter_df['magnitude'].mean()
    max_mag=filter_df['magnitude'].max()


    with col1:
        st.metric(
            label="total Events",
            value=total_events
        )
    with col2:
        st.metric(
            label="Critical(M>6.5)",
            value=critical_events
        )
    with col3:
        st.metric(
            label="Last 24H",
            value=(last_24_hours)
        )
    with col4:
        st.metric(
            label="Avg Magnitudes",
            value=(f"{avg_mag:.2f}")
        )
    with col5:
        st.metric(
            label="Max Magnitudes",
            value=(max_mag)

        )
    st.markdown("---")
    st.header("Current Alerts")
    last_24_hours = df[(df['time'] > (df['time'].max() - timedelta(hours=24))) & (df['time'] < (df['time'].max()))]
    now=datetime.now()
    alert_df=last_24_hours[last_24_hours['magnitude']>=4.5].copy()
    alert_df['time_ago']=(now-alert_df['time']).dt.total_seconds()/3600
    if len(alert_df)>0:
        st.error(f"High risk events in last 24 hours:{len(alert_df)}")
        for _,row in alert_df.head(6).iterrows():
            st.warning(f"**M{row['magnitude']:.1f}** - {row['place'][:50]} | {row['time_ago']:.1f}h ago")
        else:
            st.success("No high-risk events in last 24h")


    st.markdown("---")
    st.header("Risk Trends")
    col1,col2=st.columns(2)
    with col1:
        fig_pie=px.pie(
            filter_df['risk_level'].value_counts().reset_index(),
            values='count',
            names='risk_level',
            title='risk_Distribution'
        )
        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

        hourly = filter_df.groupby('hour').size().reset_index(name='count')
        fig_hour = px.bar(
            hourly, x='hour', y='count', title="Events by Hour"
        )
        st.plotly_chart(fig_hour, use_container_width=False)
    with col2:

        daily = filter_df.groupby('date').size().reset_index(name='count')
        fig_daily = px.line(daily, x='date', y='count', title="Daily Rate", markers=True)
        fig_daily.add_hline(y=daily['count'].mean(), line_dash="solid",line_color='red', annotation_text="Avg")
        st.plotly_chart(fig_daily, use_container_width=True)

        fig_mag = px.scatter(filter_df, x='time', y='magnitude', color='risk_level',
                             color_discrete_map={'Low': '#90EE90', 'Moderate': '#FFD700', 'High': '#FFA500',
                                                 'Critical': '#FF4500'},
                             title="Magnitude Over Time")
        st.plotly_chart(fig_mag, use_container_width=True)
    # Hazard Mapping
    st.markdown("---")
    st.header("Risk Map")
    fig_map = px.scatter_mapbox(
        filter_df, lat="latitude", lon="longitude",
        size="magnitude", color="magnitude",
        color_continuous_scale="Reds", size_max=20, opacity=0.8,
        hover_name="place", hover_data=["risk_level", "depth", "time", "tectonic_type"],
        mapbox_style="open-street-map", zoom=3
    )
    fig_map.update_layout(height=600, margin=dict(r=0, t=40, l=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)