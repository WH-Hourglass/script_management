import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import warnings
import time

# watchdog는 선택사항으로 처리
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="ZAP Enterprise Security Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Corporate Professional 디자인 CSS
st.markdown("""
<style>
    /* 기업용 배경 */
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 25%, #dee2e6 50%, #ced4da 75%, #adb5bd 100%);
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* 기업용 헤더 */
    .corporate-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 25%, #2563eb 50%, #3b82f6 75%, #60a5fa 100%);
        padding: 3rem 2rem;
        border-radius: 0;
        margin-bottom: 3rem;
        text-align: left;
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.15);
        border-bottom: 4px solid #d97706;
        position: relative;
    }
    
    .corporate-header::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 200px;
        height: 100%;
        background: linear-gradient(45deg, transparent 30%, rgba(217, 119, 6, 0.1) 70%);
    }
    
    .corporate-title {
        font-size: 2.8rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        letter-spacing: -0.5px;
    }
    
    .corporate-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        font-weight: 400;
        margin-bottom: 0;
    }
    
    .corporate-tagline {
        font-size: 0.9rem;
        color: #d97706;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 1rem;
    }
    
    /* 프로페셔널 카드 */
    .executive-card {
        background: white;
        padding: 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 20px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        border-top: 4px solid #1e40af;
        transition: all 0.3s ease;
    }
    
    .executive-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        border-top-color: #d97706;
    }
    
    .card-title-corporate {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1e40af;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-title-corporate::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(135deg, #1e40af 0%, #d97706 100%);
        border-radius: 2px;
    }
    
    /* 임원진 메트릭 */
    .executive-metric {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .executive-metric::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #1e40af 0%, #d97706 100%);
    }
    
    .executive-metric:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(30, 64, 175, 0.15);
        border-color: #1e40af;
    }
    
    .metric-number-corporate {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #1e40af;
    }
    
    .metric-label-corporate {
        font-size: 0.9rem;
        font-weight: 500;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 위험도별 기업 색상 */
    .risk-critical .metric-number-corporate { 
        color: #dc2626; 
    }
    .risk-critical::before { 
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%); 
    }
    
    .risk-high .metric-number-corporate { 
        color: #d97706; 
    }
    .risk-high::before { 
        background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%); 
    }
    
    .risk-medium .metric-number-corporate { 
        color: #2563eb; 
    }
    .risk-medium::before { 
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%); 
    }
    
    .risk-low .metric-number-corporate { 
        color: #059669; 
    }
    .risk-low::before { 
        background: linear-gradient(90deg, #059669 0%, #10b981 100%); 
    }
    
    .total-metric .metric-number-corporate { 
        color: #1e40af; 
    }
    .total-metric::before { 
        background: linear-gradient(90deg, #1e40af 0%, #d97706 100%); 
    }
    
    /* 상태 표시 */
    .status-professional {
        display: inline-flex;
        align-items: center;
        padding: 0.6rem 1.2rem;
        background: white;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        color: #374151;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.25rem;
        transition: all 0.3s ease;
    }
    
    .status-active {
        border-color: #059669;
        background: #f0fdf4;
        color: #059669;
    }
    
    .status-inactive {
        border-color: #dc2626;
        background: #fef2f2;
        color: #dc2626;
    }
    
    /* 기업용 필터 */
    .corporate-filter {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
        border-left: 4px solid #1e40af;
    }
    
    .filter-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e40af;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 정보 패널 */
    .info-panel-corporate {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #1e40af;
        border-radius: 0 8px 8px 0;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .warning-panel-corporate {
        background: #fffbeb;
        border: 1px solid #fed7aa;
        border-left: 4px solid #d97706;
        border-radius: 0 8px 8px 0;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .danger-panel-corporate {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 4px solid #dc2626;
        border-radius: 0 8px 8px 0;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* URL 표시 */
    .url-corporate {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 6px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9rem;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
        color: #1e40af;
        transition: all 0.3s ease;
    }
    
    .url-corporate:hover {
        background: #e2e8f0;
        border-color: #1e40af;
        transform: translateX(5px);
    }
    
    /* Streamlit 커스터마이징 */
    .stSelectbox > div > div {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #1e40af;
        box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
    }
    
    .stMultiSelect > div > div {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        transition: all 0.3s ease;
    }
    
    .stMultiSelect > div > div:focus-within {
        border-color: #1e40af;
        box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
    }
    
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1e40af;
        box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
    }
    
    /* 탭 스타일링 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 0.8rem 1.5rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #1e40af;
        border-color: #1e40af;
        border-bottom-color: white;
    }
</style>
""", unsafe_allow_html=True)

def get_zap_files_by_pipeline():
    """파이프라인별로 ZAP 파일들을 정리해서 반환"""
    report_dir = os.path.expanduser("~/report")
    pipelines = {}
    
    try:
        if not os.path.exists(report_dir):
            return pipelines
            
        for root, dirs, files in os.walk(report_dir):
            for file in files:
                if file.lower().startswith('zap') and file.lower().endswith('.json'):
                    full_path = os.path.join(root, file)
                    pipeline = os.path.basename(root) if root != report_dir else 'Main'
                    
                    if pipeline not in pipelines:
                        pipelines[pipeline] = []
                    
                    try:
                        file_stat = os.stat(full_path)
                        pipelines[pipeline].append({
                            'filename': file,
                            'full_path': full_path,
                            'pipeline': pipeline,
                            'last_modified': datetime.fromtimestamp(file_stat.st_mtime),
                            'size': file_stat.st_size
                        })
                    except Exception as e:
                        st.warning(f"File access error: {file} - {e}")
                        continue
        
        for pipeline in pipelines:
            pipelines[pipeline].sort(key=lambda x: x['last_modified'], reverse=True)
        
    except Exception as e:
        st.error(f"Directory scan error: {e}")
    
    return pipelines

def load_zap_file(file_path):
    """ZAP JSON 파일 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"File loading error ({file_path}): {e}")
        return None

def parse_alerts(zap_data, pipeline, filename):
    """ZAP 데이터에서 경고 정보 추출"""
    alerts = []
    
    try:
        sites = zap_data.get('site', [])
        if not isinstance(sites, list):
            sites = [sites]
        
        for site in sites:
            site_alerts = site.get('alerts', [])
            if not isinstance(site_alerts, list):
                site_alerts = [site_alerts]
            
            for alert in site_alerts:
                risk_desc = alert.get('riskdesc', 'Unknown')
                risk_level = risk_desc.split(' (')[0] if ' (' in risk_desc else risk_desc
                
                instances = alert.get('instances', [])
                if not isinstance(instances, list):
                    instances = [instances]
                
                for instance in instances:
                    alerts.append({
                        'pipeline': pipeline,
                        'filename': filename,
                        'alert_name': alert.get('name', alert.get('alert', 'Unknown')),
                        'risk_level': risk_level,
                        'confidence': risk_desc.split('(')[1].rstrip(')') if '(' in risk_desc else 'Unknown',
                        'host': site.get('@host', 'Unknown'),
                        'uri': instance.get('uri', 'Unknown'),
                        'method': instance.get('method', 'Unknown'),
                        'param': instance.get('param', ''),
                        'plugin_id': alert.get('pluginid', 'Unknown'),
                        'description': alert.get('desc', ''),
                        'solution': alert.get('solution', ''),
                        'reference': alert.get('reference', ''),
                        'cwe_id': alert.get('cweid', '-1'),
                        'attack': instance.get('attack', ''),
                        'evidence': instance.get('evidence', '')
                    })
    
    except Exception as e:
        st.error(f"Data parsing error: {e}")
    
    return alerts

def create_charts(df):
    """Corporate 스타일 차트 생성"""
    colors = {
        'High': '#dc2626',
        'Medium': '#d97706',
        'Low': '#2563eb',
        'Informational': '#059669'
    }
    
    charts = {}
    
    # Professional 파이 차트
    risk_counts = df['risk_level'].value_counts()
    if not risk_counts.empty:
        charts['risk_pie'] = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Security Risk Assessment",
            color=risk_counts.index,
            color_discrete_map=colors
        )
        charts['risk_pie'].update_layout(
            font_family="Segoe UI",
            title_font_size=18,
            title_font_color='#1e40af',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_x=0.5,
            font_color='#374151'
        )
        charts['risk_pie'].update_traces(
            textfont_size=12,
            textfont_family="Segoe UI",
            marker_line_color='white',
            marker_line_width=2
        )
    
    # Corporate 바 차트
    top_alerts = df['alert_name'].value_counts().head(10)
    if not top_alerts.empty:
        charts['top_alerts'] = px.bar(
            x=top_alerts.values,
            y=top_alerts.index,
            orientation='h',
            title="Top Security Vulnerabilities",
            labels={'x': 'Occurrences', 'y': 'Vulnerability Type'}
        )
        charts['top_alerts'].update_layout(
            font_family="Segoe UI",
            title_font_size=18,
            title_font_color='#1e40af',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_x=0.5,
            yaxis_title="",
            xaxis_title="Occurrences",
            font_color='#374151'
        )
        charts['top_alerts'].update_traces(
            marker_color='#1e40af',
            marker_line_color='white',
            marker_line_width=1
        )
    
    return charts

def main():
    # Corporate 헤더
    st.markdown("""
    <div class="corporate-header">
        <div class="corporate-title">🛡️ Hourglass Dashboard</div>
        <div class="corporate-subtitle">Advanced Vulnerability Assessment & Risk Management Platform</div>
        <div class="corporate-tagline">SECURE • RELIABLE • PROFESSIONAL</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 상태 및 컨트롤 바
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        status_class = "status-active" if WATCHDOG_AVAILABLE else "status-inactive"
        status_text = "🟢 Real-time Monitoring Active" if WATCHDOG_AVAILABLE else "🔴 Static Analysis Mode"
        st.markdown(f'<div class="status-professional {status_class}">{status_text}</div>', unsafe_allow_html=True)
    
    with col2:
        auto_refresh = st.checkbox("Auto Refresh", value=False, help="Enable automatic data refresh")
    
    with col3:
        if st.button("🔄 Refresh Data", help="Manually refresh dashboard data"):
            st.rerun()
    
    with col4:
        current_time = datetime.now().strftime('%H:%M:%S')
        st.markdown(f'<div class="status-professional">⏰ {current_time}</div>', unsafe_allow_html=True)
    
    # 데이터 로드
    pipelines = get_zap_files_by_pipeline()
    
    if not pipelines:
        st.markdown("""
        <div class="danger-panel-corporate">
            <h4 style="color: #dc2626; margin-bottom: 1rem;">⚠️ No Security Data Available</h4>
            <p style="margin-bottom: 0.5rem; color: #374151;">
                No ZAP security scan files were found in the designated report directory.
            </p>
            <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">
                Please ensure your security scanning pipeline is properly configured and scan results are stored in ~/report/ directory.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 파이프라인 선택 섹션
    st.markdown("""
    <div class="executive-card">
        <div class="card-title-corporate">📊 Pipeline Selection & Management</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 파이프라인 개요
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Available Security Pipelines:**")
        
        pipeline_options = list(pipelines.keys())
        selected_pipeline = st.selectbox(
            "Select pipeline for analysis",
            options=pipeline_options,
            label_visibility="collapsed"
        )
        
        if selected_pipeline:
            pipeline_info = pipelines[selected_pipeline]
            latest_scan = pipeline_info[0]['last_modified'].strftime('%Y-%m-%d %H:%M:%S')
            total_files = len(pipeline_info)
            
            st.markdown(f"""
            <div class="info-panel-corporate">
                <strong>Pipeline:</strong> {selected_pipeline}<br>
                <strong>Total Scans:</strong> {total_files}<br>
                <strong>Latest Scan:</strong> {latest_scan}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # 파이프라인 요약 통계
        total_pipelines = len(pipelines)
        total_files = sum(len(files) for files in pipelines.values())
        
        st.markdown(f"""
        <div class="executive-metric total-metric">
            <div class="metric-number-corporate">{total_pipelines}</div>
            <div class="metric-label-corporate">Active Pipelines</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="executive-metric">
            <div class="metric-number-corporate">{total_files}</div>
            <div class="metric-label-corporate">Total Scans</div>
        </div>
        """, unsafe_allow_html=True)
    
    if not selected_pipeline:
        return
    
    # 파일 선택 섹션
    st.markdown(f"""
    <div class="executive-card">
        <div class="card-title-corporate">📁 Scan Data Management - {selected_pipeline}</div>
    </div>
    """, unsafe_allow_html=True)
    
    pipeline_files = pipelines[selected_pipeline]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        file_options = []
        for file_info in pipeline_files:
            timestamp = file_info['last_modified'].strftime('%Y-%m-%d %H:%M')
            size_kb = file_info['size'] / 1024
            file_options.append(f"{file_info['filename']} | {timestamp} | {size_kb:.1f} KB")
        
        selected_idx = st.selectbox(
            "Select security scan report",
            options=range(len(file_options)),
            format_func=lambda x: file_options[x],
            label_visibility="collapsed"
        )
    
    with col2:
        selected_file = pipeline_files[selected_idx]
        days_ago = (datetime.now() - selected_file['last_modified']).days
        
        if days_ago == 0:
            freshness = "Today"
            panel_class = "info-panel-corporate"
        elif days_ago <= 7:
            freshness = f"{days_ago} days ago"
            panel_class = "warning-panel-corporate"
        else:
            freshness = f"{days_ago} days ago"
            panel_class = "danger-panel-corporate"
        
        st.markdown(f"""
        <div class="{panel_class}">
            <strong>Scan Freshness:</strong><br>
            {freshness}
        </div>
        """, unsafe_allow_html=True)
    
    # 데이터 분석
    selected_files = [pipeline_files[selected_idx]]
    all_alerts = []
    
    with st.spinner("Analyzing security data..."):
        for file_info in selected_files:
            zap_data = load_zap_file(file_info['full_path'])
            if zap_data:
                alerts = parse_alerts(zap_data, file_info['pipeline'], file_info['filename'])
                all_alerts.extend(alerts)
    
    if not all_alerts:
        st.markdown("""
        <div class="info-panel-corporate">
            <h4 style="color: #059669; margin-bottom: 1rem;">✅ Security Status: Clean</h4>
            <p style="margin: 0; color: #374151;">
                No security vulnerabilities were detected in the selected scan. 
                Your application appears to meet current security standards.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # DataFrame 생성
    df = pd.DataFrame(all_alerts)
    unique_alerts = df.drop_duplicates(subset=['alert_name', 'host', 'risk_level'])
    
    # Executive 메트릭 대시보드
    st.markdown("""
    <div class="executive-card">
        <div class="card-title-corporate">📈 Executive Security Overview</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        ("Total Findings", len(unique_alerts), "total-metric"),
        ("Critical", len(unique_alerts[unique_alerts['risk_level'] == 'High']), "risk-critical"),
        ("High", len(unique_alerts[unique_alerts['risk_level'] == 'Medium']), "risk-high"),
        ("Medium", len(unique_alerts[unique_alerts['risk_level'] == 'Low']), "risk-medium"),
        ("Low", len(unique_alerts[unique_alerts['risk_level'] == 'Informational']), "risk-low")
    ]
    
    for col, (label, value, css_class) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            st.markdown(f"""
            <div class="executive-metric {css_class}">
                <div class="metric-number-corporate">{value}</div>
                <div class="metric-label-corporate">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 리스크 어세스먼트
    if len(unique_alerts) > 0:
        critical_count = len(unique_alerts[unique_alerts['risk_level'] == 'High'])
        if critical_count > 0:
            st.markdown(f"""
            <div class="danger-panel-corporate">
                <h4 style="color: #dc2626; margin-bottom: 1rem;">🚨 Critical Security Alert</h4>
                <p style="margin: 0; color: #374151;">
                    <strong>{critical_count}</strong> critical security vulnerabilities require immediate attention. 
                    Please review and remediate these issues as a priority.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # 차트 분석
    st.markdown("""
    <div class="executive-card">
        <div class="card-title-corporate">📊 Security Analytics & Reporting</div>
    </div>
    """, unsafe_allow_html=True)
    
    charts = create_charts(unique_alerts)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'risk_pie' in charts:
            st.plotly_chart(charts['risk_pie'], use_container_width=True)
    
    with col2:
        if 'top_alerts' in charts:
            st.plotly_chart(charts['top_alerts'], use_container_width=True)
    
    # 필터링 시스템
    st.markdown("""
    <div class="corporate-filter">
        <div class="filter-title">🔍 Advanced Security Filtering</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_risks = st.multiselect(
            "Risk Level Filter",
            options=['High', 'Medium', 'Low', 'Informational'],
            default=[],
            help="Filter findings by risk severity level"
        )
    
    with col2:
        selected_hosts = st.multiselect(
            "Asset Filter",
            options=sorted(unique_alerts['host'].unique()),
            default=[],
            help="Filter by affected systems and hosts"
        )
    
    with col3:
        search_term = st.text_input(
            "Vulnerability Search",
            placeholder="Search vulnerability types...",
            help="Search in vulnerability names and descriptions"
        )
    
    # 필터 적용
    filtered_df = unique_alerts.copy()
    
    if selected_risks:
        filtered_df = filtered_df[filtered_df['risk_level'].isin(selected_risks)]
    
    if selected_hosts:
        filtered_df = filtered_df[filtered_df['host'].isin(selected_hosts)]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['alert_name'].str.contains(search_term, case=False, na=False)]
    
    if filtered_df.empty:
        st.markdown("""
        <div class="warning-panel-corporate">
            <h4 style="color: #d97706; margin-bottom: 1rem;">🔍 No Results Found</h4>
            <p style="margin: 0; color: #374151;">
                No security findings match your current filter criteria. 
                Please adjust your filters or clear them to view all findings.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 결과 요약
    if len(filtered_df) != len(unique_alerts):
        st.markdown(f"""
        <div class="info-panel-corporate">
            <strong>Filter Results:</strong> Displaying {len(filtered_df)} of {len(unique_alerts)} total security findings
        </div>
        """, unsafe_allow_html=True)
    
    # 데이터 테이블
    st.markdown("""
    <div class="executive-card">
        <div class="card-title-corporate">📋 Security Findings Report</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 테이블 컨트롤
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_technical = st.checkbox("Technical Details", value=False, help="Show technical columns for security team")
    
    with col2:
        sort_by = st.selectbox(
            "Sort Criteria",
            options=['risk_level', 'alert_name', 'host'],
            format_func=lambda x: {'risk_level': 'Risk Level', 'alert_name': 'Vulnerability Type', 'host': 'Affected Asset'}[x]
        )
    
    with col3:
        sort_direction = st.radio(
            "Sort Order", 
            options=['Descending', 'Ascending'],
            horizontal=True
        )
    
    # 정렬 적용
    if sort_by == 'risk_level':
        risk_order = {'High': 3, 'Medium': 2, 'Low': 1, 'Informational': 0}
        filtered_df = filtered_df.copy()
        filtered_df['risk_sort'] = filtered_df['risk_level'].map(risk_order)
        filtered_df = filtered_df.sort_values('risk_sort', ascending=(sort_direction == 'Ascending'))
        filtered_df = filtered_df.drop('risk_sort', axis=1)
    else:
        filtered_df = filtered_df.sort_values(sort_by, ascending=(sort_direction == 'Ascending'))
    
    # 테이블 표시
    if show_technical:
        display_columns = ['alert_name', 'risk_level', 'confidence', 'host', 'uri', 'method', 'plugin_id', 'cwe_id']
    else:
        display_columns = ['alert_name', 'risk_level', 'confidence', 'host', 'plugin_id']
    
    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # 상세 분석
    if len(filtered_df) > 0:
        st.markdown("""
        <div class="executive-card">
            <div class="card-title-corporate">🔬 Detailed Vulnerability Analysis</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_alert = st.selectbox(
                "Select vulnerability for detailed analysis",
                options=filtered_df['alert_name'].unique(),
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("📊 Executive Report", help="Generate executive summary report"):
                st.success("📊 Executive report generation feature will be available in the next release.")
        
        if selected_alert:
            alert_detail = filtered_df[filtered_df['alert_name'] == selected_alert].iloc[0]
            
            # 상세 정보 표시
            col1, col2 = st.columns(2)
            
            with col1:
                risk_color = {
                    'High': '#dc2626',
                    'Medium': '#d97706', 
                    'Low': '#2563eb',
                    'Informational': '#059669'
                }.get(alert_detail['risk_level'], '#6b7280')
                
                st.markdown(f"""
                <div class="info-panel-corporate">
                    <h4 style="color: #1e40af; margin-bottom: 1rem;">🎯 Vulnerability Profile</h4>
                    <p><strong>Vulnerability:</strong> {alert_detail['alert_name']}</p>
                    <p><strong>Risk Level:</strong> <span style="color: {risk_color}; font-weight: 600;">{alert_detail['risk_level']}</span></p>
                    <p><strong>Confidence:</strong> {alert_detail['confidence']}</p>
                    <p><strong>Plugin ID:</strong> {alert_detail['plugin_id']}</p>
                    <p style="margin-bottom: 0;"><strong>CWE Reference:</strong> {alert_detail['cwe_id']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                affected_hosts = filtered_df[filtered_df['alert_name'] == selected_alert]['host'].unique()
                unique_urls = filtered_df[filtered_df['alert_name'] == selected_alert]['uri'].unique()
                
                st.markdown(f"""
                <div class="info-panel-corporate">
                    <h4 style="color: #1e40af; margin-bottom: 1rem;">🌐 Impact Assessment</h4>
                    <p><strong>Affected Assets:</strong> {len(affected_hosts)}</p>
                    <p><strong>Affected Endpoints:</strong> {len(unique_urls)}</p>
                    <p><strong>Source Pipeline:</strong> {alert_detail['pipeline']}</p>
                    <p style="margin-bottom: 0;"><strong>Business Impact:</strong> <span style="color: {risk_color}; font-weight: 600;">
                        {'High' if alert_detail['risk_level'] == 'High' else 'Medium' if alert_detail['risk_level'] == 'Medium' else 'Low'}
                    </span></p>
                </div>
                """, unsafe_allow_html=True)
            
            # URL 목록
            if len(unique_urls) > 0:
                st.markdown("**🔗 Affected Endpoints:**")
                
                # 처음 5개 URL 표시
                for i, url in enumerate(unique_urls[:5]):
                    st.markdown(f"""
                    <div class="url-corporate">
                        <strong>{i+1}.</strong> {url}
                    </div>
                    """, unsafe_allow_html=True)
                
                # 더 많은 URL이 있으면 토글 버튼
                if len(unique_urls) > 5:
                    show_all_key = f"show_all_urls_{selected_alert.replace(' ', '_')}"
                    
                    if show_all_key not in st.session_state:
                        st.session_state[show_all_key] = False
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button(f"📋 View All ({len(unique_urls)} total)", key=f"btn_{show_all_key}"):
                            st.session_state[show_all_key] = not st.session_state[show_all_key]
                    
                    if st.session_state[show_all_key]:
                        st.markdown("**📊 Complete Endpoint Inventory:**")
                        for i, url in enumerate(unique_urls, 1):
                            st.markdown(f"""
                            <div class="url-corporate">
                                <strong>{i:02d}.</strong> {url}
                            </div>
                            """, unsafe_allow_html=True)
            
            # 상세 정보 탭
            if alert_detail['description'] or alert_detail['solution'] or alert_detail['reference']:
                tab1, tab2, tab3 = st.tabs(["📄 Technical Description", "🛠️ Remediation Guide", "📚 References"])
                
                with tab1:
                    if alert_detail['description']:
                        st.markdown(f"""
                        <div class="info-panel-corporate">
                            <h5 style="color: #1e40af; margin-bottom: 1rem;">Technical Analysis</h5>
                            <p style="line-height: 1.6; margin-bottom: 0;">{alert_detail['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="warning-panel-corporate">
                            <p style="margin: 0;">No detailed technical description is available for this vulnerability.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with tab2:
                    if alert_detail['solution']:
                        st.markdown(f"""
                        <div class="info-panel-corporate">
                            <h5 style="color: #1e40af; margin-bottom: 1rem;">Remediation Strategy</h5>
                            <p style="line-height: 1.6; margin-bottom: 0;">{alert_detail['solution']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="warning-panel-corporate">
                            <p style="margin: 0;">No specific remediation guidance is provided. Please consult your security team for appropriate mitigation strategies.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with tab3:
                    if alert_detail['reference']:
                        st.markdown(f"""
                        <div class="info-panel-corporate">
                            <h5 style="color: #1e40af; margin-bottom: 1rem;">External References</h5>
                            <p style="line-height: 1.6; margin-bottom: 0;">{alert_detail['reference']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="info-panel-corporate">
                            <p style="margin: 0;">No external references are available for this vulnerability.</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    # 액션 및 보고서 섹션
    st.markdown("""
    <div class="executive-card">
        <div class="card-title-corporate">📊 Reports & Data Export</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            "📄 Export CSV",
            data=csv_data,
            file_name=f"security_report_{selected_pipeline}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            help="Download findings in CSV format for analysis"
        )
    
    with col2:
        json_data = filtered_df.to_json(orient='records', indent=2)
        st.download_button(
            "📋 Export JSON",
            data=json_data,
            file_name=f"security_report_{selected_pipeline}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            help="Download findings in JSON format for integration"
        )
    
    with col3:
        if st.button("📧 Email Report", help="Email report to stakeholders"):
            st.info("📧 Email integration will be available in the enterprise version.")
    
    with col4:
        if st.button("📈 Schedule Report", help="Schedule automated reports"):
            st.info("📈 Report scheduling will be available in the enterprise version.")
    
    # 푸터
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem; 
                background: white; border-radius: 12px; 
                box-shadow: 0 2px 15px rgba(0,0,0,0.05); border: 1px solid #e5e7eb;
                border-top: 4px solid #1e40af;">
        <div style="font-size: 1.2rem; margin-bottom: 0.5rem; color: #1e40af; font-weight: 600;">
            🛡️ Enterprise Security Dashboard
        </div>
        <div style="font-size: 1rem; color: #6b7280; margin-bottom: 1rem;">
            Professional Security Analysis & Risk Management Platform
        </div>
        <div style="font-size: 0.9rem; color: #9ca3af;">
            📊 {len(df)} findings analyzed | 🏗️ {len(pipelines)} pipelines monitored | ⏰ Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        <div style="font-size: 0.8rem; color: #d1d5db; margin-top: 1rem;">
            © 2024 Enterprise Security Solutions | Confidential & Proprietary
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"System Error: {e}")
        st.error("Please contact your system administrator for assistance.")
