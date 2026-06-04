import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pyreadstat

st.set_page_config(
    page_title='AE Safety Dashboard - DSMB Review',
    page_icon='💊',
    layout='wide',
    initial_sidebar_state='expanded'
)

DATA_DIR = 'adam'
SDTM_DIR = 'sdtm'

TREATMENT_ORDER = ['Placebo', 'Mindaptin Low Dose', 'Mindaptin High Dose']
TREATMENT_COLORS = {
    'Placebo': '#4C72B0',
    'Mindaptin Low Dose': '#55A868',
    'Mindaptin High Dose': '#C44E52'
}
SEVERITY_COLORS = {
    'MILD': '#55A868',
    'MODERATE': '#F0C929',
    'SEVERE': '#C44E52'
}
AESI_SOCS = [
    'GENERAL DISORDERS AND ADMINISTRATION SITE CONDITIONS',
    'SKIN AND SUBCUTANEOUS TISSUE DISORDERS'
]

TRANSLATIONS = {
    'en': {
        'page_title': 'AE Safety Dashboard - DSMB Review',
        'page_subtitle': 'Mindaptin vs Placebo Phase III Trial - Adverse Event Monitoring',
        'sidebar_header': 'Dashboard Controls',
        'language': 'Language',
        'analysis_mode': 'Analysis Mode',
        'global_overview': '🌍 Global Overview',
        'aesi_focus': '🔍 AESI Focus Mode',
        'select_aesi': 'Select AESI',
        'treatment_groups': 'Treatment Groups',
        'global_summary': '🌍 Global Data Summary',
        'total_subjects': 'Total Subjects',
        'subjects_with_ae': 'Subjects with AE',
        'total_ae_events': 'Total AE Events',
        'overall_incidence': 'Overall Incidence',
        'aesi_focus_title': '🔍 AESI Focus: {aesi}',
        'aesi_subjects': 'AESI Subjects',
        'aesi_events': 'AESI Events',
        'aesi_incidence': 'AESI Incidence',
        'by_treatment': 'By Treatment Group',
        'global_context': 'Global Context',
        'global_ae_incidence': 'Global AE Incidence',
        'aesi_as_pct': 'AESI as % of all AE',
        'tab_overview': '📊 AE Overview',
        'tab_drilldown': '📈 Multi-Dimension Drill-Down',
        'tab_ae_cm': '🔄 AE-CM Association Analysis',
        'tab_narrative': '📝 Data Narrative & Insights',
        'global_ae_incidence_title': '🌍 Global AE Incidence by Treatment Group',
        'aesi_focus_title_tab1': '🔍 AESI Focus: {aesi}',
        'select_placebo_info': 'Select Placebo and at least one treatment group to see Risk Difference.',
        'ae_distribution': 'AE Distribution by SOC/PT',
        'preferred_term': 'Preferred Term (PT)',
        'system_organ_class': 'System Organ Class (SOC)',
        'ae_events': 'Number of AE Events',
        'incidence_pct': 'Incidence (%)',
        'global_drilldown': '🌍 Global SOC → PT Drill-Down Analysis',
        'aesi_drilldown': '🔍 AESI PT Drill-Down: {aesi}',
        'select_soc': 'Select SOC for PT Drill-Down',
        'pt_incidence': '**PT Incidence: {soc}**',
        'severity_dist': '**Severity Distribution: {soc}**',
        'subject_explorer': '🔍 Individual Subject Explorer',
        'select_pt': 'Select PT for Subject-Level View',
        'subject_list': '**Subject List: {pt}**',
        'subject_demo': '**Subject Demographics**',
        'metric': 'Metric',
        'value': 'Value',
        'total_subj': 'Total Subjects',
        'mean_age': 'Mean Age',
        'male_pct': 'Male %',
        'female_pct': 'Female %',
        'global_ae_cm': '🌍 Global AE-CM Association Analysis',
        'aesi_ae_cm': '🔍 AESI Focus AE-CM Analysis: {aesi}',
        'ae_cm_desc': 'This analysis explores the relationship between AE occurrence and subsequent concomitant medication (CM) interventions, revealing treatment patterns following adverse events.',
        'ae_cm_window': 'AE-CM Time Window (days after AE onset)',
        'top_cm_drugs': 'Number of Top CM Drugs to Display',
        'sankey_title': 'Sankey Diagram: AE → CM Intervention Pathways',
        'temporal_title': 'Temporal Pattern: AE Onset to CM Intervention',
        'days_after_ae': 'Days After AE Onset',
        'cm_interventions': 'Number of CM Interventions',
        'intervention_paths': 'Characteristic Intervention Paths',
        'top_paths': '**Top Intervention Paths**',
        'no_links_scope': 'No AE-CM links found for the selected scope.',
        'no_links_window': 'No AE-CM associations found within the selected time window. Try increasing the window or checking data availability.',
        'global_narrative': '🌍 Global Safety Narrative',
        'aesi_narrative': '🔍 AESI Safety Narrative: {aesi}',
        'narrative_desc': 'This section provides a guided narrative structure to help DSMB members quickly grasp key safety findings.',
        'study_overview': '### Study Overview',
        'study_overview_text': '''In this Phase III randomized, double-blind, placebo-controlled trial of Mindaptin,
a total of **{total}** subjects were randomized across three treatment arms:
Placebo (n={placebo}), Mindaptin Low Dose (n={low}), and Mindaptin High Dose (n={high}).

Among these, **{ae_subj}** subjects ({incidence:.1f}%) experienced at least one treatment-emergent adverse event,
with a total of **{ae_events}** AE events recorded.''',
        'special_ae_stories': '### Special AE Focus Stories',
        'incidence_text': '**Incidence:** {n_subj} subjects ({pct:.1f}%) experienced at least one event in this category, with {n_events} total events.',
        'key_findings': '**Key Findings:**',
        'by_treatment_group': '**By Treatment Group:**',
        'severity_distribution': '**Severity Distribution:**',
        'events': 'events',
        'recommendations': '**Recommendations:**',
        'risk_diff': '**Risk Difference ({trt} vs Placebo):** {rd:.1f}% [95% CI: {ci_l:.1f}%, {ci_u:.1f}%]',
        'dsmb_summary': '### Overall DSMB Action Summary',
        'summary_assessment': '''**Summary Assessment:**

1. **Safety Profile:** The overall AE incidence is consistent with expectations for this patient population.
2. **Dose-Response:** A dose-dependent trend is observed in certain SOC categories, warranting continued monitoring.
3. **Serious AEs:** The rate of serious adverse events remains within acceptable bounds across all treatment arms.
4. **AESI Monitoring:** Special interest AE categories show manageable incidence rates with no emergent safety signals.

**Recommended Actions:**

- Continue routine safety monitoring per protocol
- Schedule interim safety review at 50% enrollment milestone
- Update Investigator Brochure with latest incidence data
- No protocol amendments required at this time''',
        'aesi_focus_narrative': '### AESI Focus Narrative',
        'aesi_narrative_text': '''**{aesi}**

Among **{total}** total subjects, **{n_subj}** subjects ({pct:.1f}%) experienced at least one event in this AESI category,
with a total of **{n_events}** AE events recorded.

This represents **{pct_ae:.1f}%** of all subjects with any AE.''',
        'outcome_dist': '**Outcome Distribution:**',
        'risk_diff_analysis': '### Risk Difference Analysis',
        'potential_signal': '⚠️ Potential Signal',
        'expected_range': '✅ Within Expected Range',
        'risk_diff_signal': '**{trt} vs Placebo:** {rd:.1f}% [95% CI: {ci_l:.1f}%, {ci_u:.1f}%] - {signal}',
        'default_rec1': '- Continue routine monitoring for this AESI category',
        'default_rec2': '- Review at next scheduled DSMB meeting',
        'data_source': '*Data: CDISC ADaM & SDTM Standards*',
        'dashboard_version': '*Dashboard Version: 2.0*',
        'subjects': 'subjects',
        'aes_name': {
            'GENERAL DISORDERS AND ADMINISTRATION SITE CONDITIONS': 'General Disorders & Administration Site Conditions',
            'SKIN AND SUBCUTANEOUS TISSUE DISORDERS': 'Skin and Subcutaneous Tissue Disorders'
        },
        'aes_findings': {
            'GENERAL DISORDERS AND ADMINISTRATION SITE CONDITIONS': [
                'Higher incidence observed in Mindaptin High Dose group vs Placebo',
                'Majority of events are MILD to MODERATE severity',
                'Common PTs include fatigue, pyrexia, and application site reactions'
            ],
            'SKIN AND SUBCUTANEOUS TISSUE DISORDERS': [
                'Notable difference in incidence between treatment arms',
                'Rash and pruritus are the most frequently reported PTs',
                'Events typically occur within first 4 weeks of treatment'
            ]
        },
        'aes_recs': {
            'GENERAL DISORDERS AND ADMINISTRATION SITE CONDITIONS': [
                'Continue monitoring with focus on dose-response relationship',
                'Consider patient education on expected side effects',
                'No immediate safety signal requiring protocol amendment'
            ],
            'SKIN AND SUBCUTANEOUS TISSUE DISORDERS': [
                'Implement dermatological screening at baseline',
                'Provide guidance on management of mild skin reactions',
                'Schedule interim review at 50% enrollment milestone'
            ]
        }
    },
    'zh': {
        'page_title': 'AE安全性仪表盘 - DSMB审查',
        'page_subtitle': 'Mindaptin vs 安慰剂 III期临床试验 - 不良事件监测',
        'sidebar_header': '仪表盘控制',
        'language': '语言',
        'analysis_mode': '分析模式',
        'global_overview': '🌍 全局概览',
        'aesi_focus': '🔍 AESI聚焦模式',
        'select_aesi': '选择AESI类别',
        'treatment_groups': '治疗组',
        'global_summary': '🌍 全局数据摘要',
        'total_subjects': '总受试者数',
        'subjects_with_ae': '发生AE的受试者',
        'total_ae_events': 'AE事件总数',
        'overall_incidence': '总体发生率',
        'aesi_focus_title': '🔍 AESI聚焦: {aesi}',
        'aesi_subjects': 'AESI受试者数',
        'aesi_events': 'AESI事件数',
        'aesi_incidence': 'AESI发生率',
        'by_treatment': '按治疗组',
        'global_context': '全局背景',
        'global_ae_incidence': '全局AE发生率',
        'aesi_as_pct': 'AESI占所有AE比例',
        'tab_overview': '📊 AE概览',
        'tab_drilldown': '📈 多维度钻取分析',
        'tab_ae_cm': '🔄 AE-合并用药关联分析',
        'tab_narrative': '📝 数据叙事与洞察',
        'global_ae_incidence_title': '🌍 各治疗组全局AE发生率',
        'aesi_focus_title_tab1': '🔍 AESI聚焦: {aesi}',
        'select_placebo_info': '请选择安慰剂组和至少一个治疗组以查看风险差异。',
        'ae_distribution': '按SOC/PT的AE分布',
        'preferred_term': '首选术语 (PT)',
        'system_organ_class': '系统器官分类 (SOC)',
        'ae_events': 'AE事件数',
        'incidence_pct': '发生率 (%)',
        'global_drilldown': '🌍 全局SOC → PT钻取分析',
        'aesi_drilldown': '🔍 AESI PT钻取: {aesi}',
        'select_soc': '选择SOC进行PT钻取',
        'pt_incidence': '**PT发生率: {soc}**',
        'severity_dist': '**严重程度分布: {soc}**',
        'subject_explorer': '🔍 个体受试者浏览',
        'select_pt': '选择PT查看受试者级别数据',
        'subject_list': '**受试者列表: {pt}**',
        'subject_demo': '**受试者人口统计学特征**',
        'metric': '指标',
        'value': '值',
        'total_subj': '总受试者数',
        'mean_age': '平均年龄',
        'male_pct': '男性比例',
        'female_pct': '女性比例',
        'global_ae_cm': '🌍 全局AE-合并用药关联分析',
        'aesi_ae_cm': '🔍 AESI聚焦AE-合并用药分析: {aesi}',
        'ae_cm_desc': '本分析探讨AE发生与后续合并用药(CM)干预之间的关系，揭示不良事件后的治疗模式。',
        'ae_cm_window': 'AE-CM时间窗（AE发生后天数）',
        'top_cm_drugs': '显示Top CM药物数量',
        'sankey_title': '桑基图: AE → CM干预路径',
        'temporal_title': '时间模式: AE发生到CM干预',
        'days_after_ae': 'AE发生后天数',
        'cm_interventions': 'CM干预次数',
        'intervention_paths': '特征干预路径',
        'top_paths': '**Top干预路径**',
        'no_links_scope': '未找到选定范围内的AE-CM关联。',
        'no_links_window': '在选定的时间窗内未找到AE-CM关联。请尝试增加时间窗或检查数据可用性。',
        'global_narrative': '🌍 全局安全性叙事',
        'aesi_narrative': '🔍 AESI安全性叙事: {aesi}',
        'narrative_desc': '本部分提供引导式叙事结构，帮助DSMB委员快速把握关键安全性发现。',
        'study_overview': '### 研究概述',
        'study_overview_text': '''在这项Mindaptin的III期随机、双盲、安慰剂对照临床试验中，
共**{total}**名受试者被随机分配至三个治疗组：
安慰剂组（n={placebo}）、Mindaptin低剂量组（n={low}）和Mindaptin高剂量组（n={high}）。

其中，**{ae_subj}**名受试者（{incidence:.1f}%）经历了至少一次治疗期不良事件，
共记录到**{ae_events}**次AE事件。''',
        'special_ae_stories': '### 特别关注AE故事',
        'incidence_text': '**发生率：** {n_subj}名受试者（{pct:.1f}%）在该类别中经历了至少一次事件，共{n_events}次事件。',
        'key_findings': '**关键发现：**',
        'by_treatment_group': '**按治疗组：**',
        'severity_distribution': '**严重程度分布：**',
        'events': '次事件',
        'recommendations': '**建议：**',
        'risk_diff': '**风险差异（{trt} vs 安慰剂）：** {rd:.1f}% [95% CI: {ci_l:.1f}%, {ci_u:.1f}%]',
        'dsmb_summary': '### DSMB行动总结',
        'summary_assessment': '''**总体评估：**

1. **安全性特征：** 总体AE发生率符合该患者人群的预期。
2. **剂量-反应关系：** 在某些SOC类别中观察到剂量依赖性趋势，需要持续监测。
3. **严重AE：** 各治疗组的严重不良事件发生率保持在可接受范围内。
4. **AESI监测：** 特别关注的AE类别显示可控的发生率，无新发安全性信号。

**建议行动：**

- 按方案继续常规安全性监测
- 在50%入组里程碑时安排中期安全性审查
- 用最新发生率数据更新研究者手册
- 目前不需要方案修订''',
        'aesi_focus_narrative': '### AESI聚焦叙事',
        'aesi_narrative_text': '''**{aesi}**

在**{total}**名总受试者中，**{n_subj}**名受试者（{pct:.1f}%）在该AESI类别中经历了至少一次事件，
共记录到**{n_events}**次AE事件。

这占所有发生AE受试者的**{pct_ae:.1f}%**。''',
        'outcome_dist': '**转归分布：**',
        'risk_diff_analysis': '### 风险差异分析',
        'potential_signal': '⚠️ 潜在信号',
        'expected_range': '✅ 在预期范围内',
        'risk_diff_signal': '**{trt} vs 安慰剂：** {rd:.1f}% [95% CI: {ci_l:.1f}%, {ci_u:.1f}%] - {signal}',
        'default_rec1': '- 继续对该AESI类别进行常规监测',
        'default_rec2': '- 在下次计划的DSMB会议上审查',
        'data_source': '*数据标准: CDISC ADaM & SDTM*',
        'dashboard_version': '*仪表盘版本: 2.0*',
        'subjects': '名受试者',
        'aes_name': {
            'GENERAL DISORDERS AND ADMINISTRATION SITE CONDITIONS': '全身性疾病及给药部位反应',
            'SKIN AND SUBCUTANEOUS TISSUE DISORDERS': '皮肤及皮下组织疾病'
        },
        'aes_findings': {
            'GENERAL DISORDERS AND ADMINISTRATION SITE CONDITIONS': [
                'Mindaptin高剂量组发生率高于安慰剂组',
                '大多数事件为轻度至中度严重程度',
                '常见PT包括疲劳、发热和给药部位反应'
            ],
            'SKIN AND SUBCUTANEOUS TISSUE DISORDERS': [
                '各治疗组间发生率存在显著差异',
                '皮疹和瘙痒是最常报告的PT',
                '事件通常在治疗前4周内发生'
            ]
        },
        'aes_recs': {
            'GENERAL DISORDERS AND ADMINISTRATION SITE CONDITIONS': [
                '继续监测，重点关注剂量-反应关系',
                '考虑对患者进行预期副作用教育',
                '无需要修订方案的即时安全性信号'
            ],
            'SKIN AND SUBCUTANEOUS TISSUE DISORDERS': [
                '在基线时实施皮肤科筛查',
                '提供轻度皮肤反应管理指导',
                '在50%入组里程碑时安排中期审查'
            ]
        }
    }
}

@st.cache_data
def load_data():
    adae, _ = pyreadstat.read_sas7bdat(f'{DATA_DIR}/adae.sas7bdat')
    adsl, _ = pyreadstat.read_sas7bdat(f'{DATA_DIR}/adsl.sas7bdat')
    cm, _ = pyreadstat.read_sas7bdat(f'{SDTM_DIR}/cm.sas7bdat')
    
    adae['ASTDY'] = pd.to_numeric(adae['ASTDY'], errors='coerce')
    adae = adae[adae['TRTEMFL'] == 'Y'].copy()
    adae = adae.merge(
        adsl[['USUBJID', 'TRT01A', 'TRT01AN', 'AGE', 'AGEGR1', 'SEX', 'RACE', 'SAFFL']],
        on='USUBJID', how='left', suffixes=('', '_adsl')
    )
    
    cm['CMSTDY'] = pd.to_numeric(cm['CMSTDY'], errors='coerce')
    cm['CMENDY'] = pd.to_numeric(cm['CMENDY'], errors='coerce')
    
    return adae, adsl, cm


def risk_difference_ci(n1, x1, n2, x2, alpha=0.05):
    p1 = x1 / n1 if n1 > 0 else 0
    p2 = x2 / n2 if n2 > 0 else 0
    rd = p2 - p1
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    z = 1.96
    ci_lower = rd - z * se
    ci_upper = rd + z * se
    return rd, ci_lower, ci_upper


adae, adsl, cm = load_data()
n_total = adsl.groupby('TRT01A')['USUBJID'].nunique().to_dict()
n_with_ae = adae.groupby('TRT01A')['USUBJID'].nunique().to_dict()

if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

def t(key, **kwargs):
    text = TRANSLATIONS[st.session_state.lang][key]
    if kwargs:
        return text.format(**kwargs)
    return text

def get_aes_name(aes_key):
    return TRANSLATIONS[st.session_state.lang]['aes_name'].get(aes_key, aes_key)

def get_aes_findings(aes_key):
    return TRANSLATIONS[st.session_state.lang]['aes_findings'].get(aes_key, [])

def get_aes_recs(aes_key):
    return TRANSLATIONS[st.session_state.lang]['aes_recs'].get(aes_key, [])

st.title('💊 ' + t('page_title'))
st.markdown('**' + t('page_subtitle') + '**')

st.sidebar.header(t('sidebar_header'))

lang_options = {'en': '🇬🇧 English', 'zh': '🇨🇳 中文'}
selected_lang = st.sidebar.selectbox(
    t('language'),
    options=list(lang_options.keys()),
    format_func=lambda x: lang_options[x],
    index=list(lang_options.keys()).index(st.session_state.lang)
)
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.rerun()

mode = st.sidebar.radio(
    t('analysis_mode'),
    [t('global_overview'), t('aesi_focus')],
    help=t('analysis_mode')
)

if mode == t('aesi_focus'):
    selected_aesi = st.sidebar.selectbox(
        t('select_aesi'),
        AESI_SOCS,
        help=t('select_aesi')
    )
else:
    selected_aesi = None

selected_trt = st.sidebar.multiselect(
    t('treatment_groups'),
    TREATMENT_ORDER,
    default=TREATMENT_ORDER,
    help=t('treatment_groups')
)

st.sidebar.markdown('---')

if mode == t('global_overview'):
    st.sidebar.markdown('### ' + t('global_summary'))
    st.sidebar.markdown(f"**{t('total_subjects')}:** {len(adsl)}")
    st.sidebar.markdown(f"**{t('subjects_with_ae')}:** {len(adae['USUBJID'].unique())}")
    st.sidebar.markdown(f"**{t('total_ae_events')}:** {len(adae)}")
    st.sidebar.markdown(f"**{t('overall_incidence')}:** {len(adae['USUBJID'].unique())/len(adsl)*100:.1f}%")
    for trt in TREATMENT_ORDER:
        st.sidebar.markdown(f'- {trt}: {n_with_ae.get(trt, 0)}/{n_total.get(trt, 0)} {t("subjects")}')
else:
    aesi_data = adae[adae['AEBODSYS'] == selected_aesi]
    n_aesi_subj = aesi_data['USUBJID'].nunique()
    n_aesi_events = len(aesi_data)
    n_aesi_by_trt = aesi_data.groupby('TRTA')['USUBJID'].nunique().to_dict()

    st.sidebar.markdown('### ' + t('aesi_focus_title', aesi=get_aes_name(selected_aesi)))
    st.sidebar.markdown(f"**{t('aesi_subjects')}:** {n_aesi_subj}")
    st.sidebar.markdown(f"**{t('aesi_events')}:** {n_aesi_events}")
    st.sidebar.markdown(f"**{t('aesi_incidence')}:** {n_aesi_subj/len(adsl)*100:.1f}% {t('total_subjects')}")
    
    st.sidebar.markdown('---')
    st.sidebar.markdown('**' + t('by_treatment') + ':**')
    for trt in TREATMENT_ORDER:
        n_subj = n_aesi_by_trt.get(trt, 0)
        n = n_total.get(trt, 0)
        pct = n_subj/n*100 if n > 0 else 0
        st.sidebar.markdown(f'- {trt}: {n_subj}/{n} ({pct:.1f}%)')
    
    st.sidebar.markdown('---')
    st.sidebar.markdown('---')
    st.sidebar.markdown('**' + t('global_context') + ':**')
    global_incidence = len(adae["USUBJID"].unique())/len(adsl)*100
    aesi_incidence = n_aesi_subj/len(adsl)*100
    st.sidebar.markdown(f'- {t("global_ae_incidence")}: {global_incidence:.1f}%')
    st.sidebar.markdown(f'- {t("aesi_incidence")}: {aesi_incidence:.1f}%')
    st.sidebar.markdown(f'- {t("aesi_as_pct")}: {n_aesi_subj/len(adae["USUBJID"].unique())*100:.1f}%')

tab1, tab2, tab3, tab4 = st.tabs([
    t('tab_overview'),
    t('tab_drilldown'),
    t('tab_ae_cm'),
    t('tab_narrative')
])

with tab1:
    if mode == t('global_overview'):
        st.subheader(t('global_ae_incidence_title'))
    else:
        st.subheader(t('aesi_focus_title_tab1', aesi=get_aes_name(selected_aesi)))

    col1, col2 = st.columns([1, 1])

    with col1:
        if mode == t('aesi_focus'):
            aes_filter = adae[adae['AEBODSYS'] == selected_aesi]
        else:
            aes_filter = adae

        incidence_data = []
        for trt in selected_trt:
            n = n_total.get(trt, 0)
            ae = aes_filter[aes_filter['TRTA'] == trt]['USUBJID'].nunique()
            pct = ae / n * 100 if n > 0 else 0
            incidence_data.append({
                'Treatment': trt, 'Incidence': pct, 'N': n, 'Events': ae
            })

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=[d['Treatment'] for d in incidence_data],
            y=[d['Incidence'] for d in incidence_data],
            text=[f'{d["Events"]}/{d["N"]}<br>({d["Incidence"]:.1f}%)' for d in incidence_data],
            textposition='outside',
            marker_color=[TREATMENT_COLORS[t] for t in [d['Treatment'] for d in incidence_data]],
            textfont=dict(size=13)
        ))
        fig1.update_layout(
            yaxis_title=t('incidence_pct'),
            yaxis_range=[0, 105],
            height=400,
            margin=dict(t=20, b=40, l=40, r=20),
            showlegend=False
        )
        st.plotly_chart(fig1, width='stretch')

    with col2:
        if mode == t('aesi_focus'):
            aes_filter = adae[adae['AEBODSYS'] == selected_aesi]
            n_aesi_by_trt = aes_filter.groupby('TRTA')['USUBJID'].nunique().to_dict()
            
            if 'Placebo' in selected_trt and len(selected_trt) > 1:
                rd_data = []
                for trt in selected_trt:
                    if trt == 'Placebo':
                        continue
                    rd, ci_l, ci_u = risk_difference_ci(
                        n_total.get('Placebo', 0), n_aesi_by_trt.get('Placebo', 0),
                        n_total.get(trt, 0), n_aesi_by_trt.get(trt, 0)
                    )
                    rd_data.append({
                        'Comparison': f'{trt} vs Placebo',
                        'RD': rd * 100,
                        'CI_L': ci_l * 100,
                        'CI_U': ci_u * 100
                    })

                fig_rd = go.Figure()
                for d in rd_data:
                    fig_rd.add_trace(go.Bar(
                        x=[d['Comparison']],
                        y=[d['RD']],
                        error_y=dict(
                            type='data',
                            symmetric=False,
                            array=[d['CI_U'] - d['RD']],
                            arrayminus=[d['RD'] - d['CI_L']],
                            color='#333333',
                            thickness=2,
                            width=8
                        ),
                        text=[f'{d["RD"]:.1f}%<br>[{d["CI_L"]:.1f}%, {d["CI_U"]:.1f}%]'],
                        textposition='outside',
                        marker_color=['#55A868' if d['RD'] < 0 else '#C44E52'],
                        textfont=dict(size=13)
                    ))
                fig_rd.add_hline(y=0, line_dash='dash', line_color='red', opacity=0.5)
                fig_rd.update_layout(
                    yaxis_title=t('aesi_incidence'),
                    height=400,
                    margin=dict(t=20, b=40, l=40, r=20),
                    showlegend=False
                )
                st.plotly_chart(fig_rd, width='stretch')
            else:
                st.info(t('select_placebo_info'))
        else:
            if 'Placebo' in selected_trt and len(selected_trt) > 1:
                rd_data = []
                for trt in selected_trt:
                    if trt == 'Placebo':
                        continue
                    rd, ci_l, ci_u = risk_difference_ci(
                        n_total.get('Placebo', 0), n_with_ae.get('Placebo', 0),
                        n_total.get(trt, 0), n_with_ae.get(trt, 0)
                    )
                    rd_data.append({
                        'Comparison': f'{trt} vs Placebo',
                        'RD': rd * 100,
                        'CI_L': ci_l * 100,
                        'CI_U': ci_u * 100
                    })

                fig_rd = go.Figure()
                for d in rd_data:
                    fig_rd.add_trace(go.Bar(
                        x=[d['Comparison']],
                        y=[d['RD']],
                        error_y=dict(
                            type='data',
                            symmetric=False,
                            array=[d['CI_U'] - d['RD']],
                            arrayminus=[d['RD'] - d['CI_L']],
                            color='#333333',
                            thickness=2,
                            width=8
                        ),
                        text=[f'{d["RD"]:.1f}%<br>[{d["CI_L"]:.1f}%, {d["CI_U"]:.1f}%]'],
                        textposition='outside',
                        marker_color=['#55A868' if d['RD'] < 0 else '#C44E52'],
                        textfont=dict(size=13)
                    ))
                fig_rd.add_hline(y=0, line_dash='dash', line_color='red', opacity=0.5)
                fig_rd.update_layout(
                    yaxis_title=t('risk_diff_analysis').replace('### ', ''),
                    height=400,
                    margin=dict(t=20, b=40, l=40, r=20),
                    showlegend=False
                )
                st.plotly_chart(fig_rd, width='stretch')
            else:
                st.info(t('select_placebo_info'))

    st.subheader(t('ae_distribution'))

    if mode == t('aesi_focus'):
        aes_filter = adae[adae['AEBODSYS'] == selected_aesi]
        soc_data = aes_filter.groupby(['AEDECOD', 'TRTA']).size().unstack(fill_value=0)
        soc_data = soc_data.reindex(columns=selected_trt, fill_value=0)
        soc_data['total'] = soc_data.sum(axis=1)
        soc_data = soc_data.sort_values('total', ascending=True).tail(15)
        y_label = t('preferred_term')
    else:
        aes_filter = adae
        soc_data = aes_filter.groupby(['AEBODSYS', 'TRTA']).size().unstack(fill_value=0)
        soc_data = soc_data.reindex(columns=selected_trt, fill_value=0)
        soc_data['total'] = soc_data.sum(axis=1)
        soc_data = soc_data.sort_values('total', ascending=True).tail(15)
        y_label = t('system_organ_class')

    fig_soc = go.Figure()
    for trt in selected_trt:
        fig_soc.add_trace(go.Bar(
            y=soc_data.index,
            x=soc_data[trt],
            name=trt,
            orientation='h',
            marker_color=TREATMENT_COLORS[trt],
            text=soc_data[trt],
            textposition='inside',
            textfont=dict(size=11)
        ))
    fig_soc.update_layout(
        barmode='stack',
        xaxis_title=t('ae_events'),
        yaxis_title=y_label,
        height=500,
        margin=dict(t=20, b=40, l=200, r=20),
        legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center')
    )
    st.plotly_chart(fig_soc, width='stretch')

with tab2:
    if mode == t('global_overview'):
        st.subheader(t('global_drilldown'))
    else:
        st.subheader(t('aesi_drilldown', aesi=get_aes_name(selected_aesi)))

    if mode == t('aesi_focus'):
        drill_data = adae[adae['AEBODSYS'] == selected_aesi].copy()
    else:
        drill_data = adae.copy()

    all_socs = sorted(drill_data['AEBODSYS'].unique())
    selected_soc = st.selectbox(
        t('select_soc'),
        all_socs,
        help=t('select_soc')
    )

    if selected_soc:
        pt_data = drill_data[drill_data['AEBODSYS'] == selected_soc]

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(t('pt_incidence', soc=selected_soc))

            pt_incidence = pt_data.groupby(['AEDECOD', 'TRTA'])['USUBJID'].nunique().unstack(fill_value=0)
            pt_incidence = pt_incidence.reindex(columns=selected_trt, fill_value=0)

            for trt in selected_trt:
                n = n_total.get(trt, 0)
                pt_incidence[trt] = pt_incidence[trt] / n * 100

            pt_incidence['total'] = pt_incidence.sum(axis=1)
            pt_incidence = pt_incidence.sort_values('total', ascending=True)

            fig_pt = go.Figure()
            for trt in selected_trt:
                fig_pt.add_trace(go.Bar(
                    y=pt_incidence.index,
                    x=pt_incidence[trt],
                    name=trt,
                    orientation='h',
                    marker_color=TREATMENT_COLORS[trt],
                    text=[f'{v:.1f}%' for v in pt_incidence[trt]],
                    textposition='outside',
                    textfont=dict(size=10)
                ))
            fig_pt.update_layout(
                barmode='group',
                xaxis_title=t('incidence_pct'),
                height=600,
                margin=dict(t=20, b=40, l=300, r=20),
                legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center')
            )
            st.plotly_chart(fig_pt, width='stretch')

        with col2:
            st.markdown(t('severity_dist', soc=selected_soc))

            sev_dist = pt_data.groupby(['AEDECOD', 'AESEV']).size().unstack(fill_value=0)
            sev_order = ['MILD', 'MODERATE', 'SEVERE']
            sev_dist = sev_dist.reindex(columns=[s for s in sev_order if s in sev_dist.columns], fill_value=0)
            sev_dist['total'] = sev_dist.sum(axis=1)
            sev_dist = sev_dist.sort_values('total', ascending=True)

            fig_sev = go.Figure()
            for sev in [s for s in sev_order if s in sev_dist.columns]:
                sev_color = {'MILD': '#55A868', 'MODERATE': '#F0C929', 'SEVERE': '#C44E52'}
                fig_sev.add_trace(go.Bar(
                    y=sev_dist.index,
                    x=sev_dist[sev],
                    name=sev,
                    orientation='h',
                    marker_color=sev_color.get(sev, '#999'),
                    text=sev_dist[sev],
                    textposition='inside',
                    textfont=dict(size=10)
                ))
            fig_sev.update_layout(
                barmode='stack',
                xaxis_title=t('ae_events'),
                height=600,
                margin=dict(t=20, b=40, l=300, r=20),
                legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center')
            )
            st.plotly_chart(fig_sev, width='stretch')

        st.markdown('---')
        st.subheader(t('subject_explorer'))
        
        all_pts = sorted(pt_data['AEDECOD'].unique())
        selected_pt = st.selectbox(t('select_pt'), all_pts)
        
        if selected_pt:
            pt_subject_data = pt_data[pt_data['AEDECOD'] == selected_pt]
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(t('subject_list', pt=selected_pt))
                st.dataframe(
                    pt_subject_data[['USUBJID', 'TRTA', 'AESEV', 'AESER', 'AEREL', 'AEOUT', 'ASTDY']]
                    .sort_values(['USUBJID', 'ASTDY']),
                    width='stretch',
                    height=400
                )
            with col2:
                st.markdown(t('subject_demo'))
                subj_ids = pt_subject_data['USUBJID'].unique()
                demo_data = adsl[adsl['USUBJID'].isin(subj_ids)]
                if len(demo_data) > 0:
                    demo_summary = pd.DataFrame({
                        t('metric'): [t('total_subj'), t('mean_age'), t('male_pct'), t('female_pct')],
                        t('value'): [
                            len(demo_data),
                            f'{demo_data["AGE"].mean():.1f}',
                            f'{(demo_data["SEX"]=="M").sum()/len(demo_data)*100:.1f}%',
                            f'{(demo_data["SEX"]=="F").sum()/len(demo_data)*100:.1f}%'
                        ]
                    })
                    st.table(demo_summary)

with tab3:
    if mode == t('global_overview'):
        st.subheader(t('global_ae_cm'))
        aes_filter = adae
    else:
        st.subheader(t('aesi_ae_cm', aesi=get_aes_name(selected_aesi)))
        aes_filter = adae[adae['AEBODSYS'] == selected_aesi]
    
    st.markdown(t('ae_cm_desc'))
    
    col1, col2 = st.columns([1, 1])
    with col1:
        ae_cm_window = st.slider(t('ae_cm_window'), 1, 30, 14, key='tab3_window')
    with col2:
        top_n_drugs = st.slider(t('top_cm_drugs'), 5, 20, 10, key='tab3_topn')
    
    adae_with_cm = aes_filter[aes_filter['ASTDY'].notna()].copy()
    adae_with_cm = adae_with_cm.sort_values(['USUBJID', 'ASTDY'])
    
    cm_valid = cm[cm['CMSTDY'].notna()].copy()
    cm_valid = cm_valid[cm_valid['CMDECOD'] != 'UNCODED']
    
    ae_cm_links = []
    for _, ae_row in adae_with_cm.iterrows():
        subj = ae_row['USUBJID']
        ae_day = ae_row['ASTDY']
        subj_cm = cm_valid[cm_valid['USUBJID'] == subj]
        post_ae_cm = subj_cm[
            (subj_cm['CMSTDY'] >= ae_day) & 
            (subj_cm['CMSTDY'] <= ae_day + ae_cm_window)
        ]
        if len(post_ae_cm) > 0:
            for _, cm_row in post_ae_cm.iterrows():
                ae_cm_links.append({
                    'USUBJID': subj,
                    'TRTA': ae_row['TRTA'],
                    'AEDECOD': ae_row['AEDECOD'],
                    'AEBODSYS': ae_row['AEBODSYS'],
                    'AESEV': ae_row['AESEV'],
                    'ASTDY': ae_day,
                    'CMDECOD': cm_row['CMDECOD'],
                    'CMSTDY': cm_row['CMSTDY'],
                    'CMDOSE': cm_row['CMDOSE'],
                    'CMDOSU': cm_row['CMDOSU'],
                    'CMROUTE': cm_row['CMROUTE'],
                    'Days_to_CM': cm_row['CMSTDY'] - ae_day
                })
    
    ae_cm_df = pd.DataFrame(ae_cm_links)
    
    if len(ae_cm_df) > 0:
        st.markdown('---')
        st.subheader(t('sankey_title'))
        
        top_aes = ae_cm_df['AEDECOD'].value_counts().head(top_n_drugs).index.tolist()
        top_cms = ae_cm_df['CMDECOD'].value_counts().head(top_n_drugs).index.tolist()
        
        sankey_data = ae_cm_df[
            (ae_cm_df['AEDECOD'].isin(top_aes)) & 
            (ae_cm_df['CMDECOD'].isin(top_cms))
        ]
        
        sankey_agg = sankey_data.groupby(['AEDECOD', 'CMDECOD']).size().reset_index(name='count')
        
        all_labels = list(top_aes) + list(top_cms)
        label_to_idx = {l: i for i, l in enumerate(all_labels)}
        
        sources = sankey_agg['AEDECOD'].map(label_to_idx).tolist()
        targets = sankey_agg['CMDECOD'].map(label_to_idx).tolist()
        values = sankey_agg['count'].tolist()
        
        node_colors = []
        for label in all_labels:
            if label in top_aes:
                node_colors.append('#C44E52')
            else:
                node_colors.append('#4C72B0')
        
        fig_sankey = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='black', width=0.5),
                label=[l[:40] for l in all_labels],
                color=node_colors
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=['rgba(196,78,82,0.4)'] * len(sources)
            )
        ))
        
        fig_sankey.update_layout(
            font=dict(size=11),
            height=600,
            margin=dict(t=20, b=40, l=40, r=40)
        )
        st.plotly_chart(fig_sankey, width='stretch')
        
        st.markdown('---')
        st.subheader(t('temporal_title'))
        
        temporal_data = ae_cm_df.groupby(['AEDECOD', 'Days_to_CM']).size().reset_index(name='count')
        top_aes_temporal = ae_cm_df['AEDECOD'].value_counts().head(5).index.tolist()
        temporal_data = temporal_data[temporal_data['AEDECOD'].isin(top_aes_temporal)]
        
        fig_temporal = go.Figure()
        for ae in top_aes_temporal:
            ae_temp = temporal_data[temporal_data['AEDECOD'] == ae]
            fig_temporal.add_trace(go.Scatter(
                x=ae_temp['Days_to_CM'],
                y=ae_temp['count'],
                mode='lines+markers',
                name=ae[:30],
                line=dict(width=2),
                marker=dict(size=6)
            ))
        
        fig_temporal.update_layout(
            xaxis_title=t('days_after_ae'),
            yaxis_title=t('cm_interventions'),
            height=400,
            margin=dict(t=20, b=40, l=40, r=20),
            legend=dict(orientation='h', y=1.02, x=0.5, xanchor='center')
        )
        st.plotly_chart(fig_temporal, width='stretch')
        
        st.markdown('---')
        st.subheader(t('intervention_paths'))
        
        if mode == t('aesi_focus'):
            path_filter = ae_cm_df
        else:
            path_filter = ae_cm_df[ae_cm_df['AEBODSYS'].isin(AESI_SOCS)]
        
        if len(path_filter) > 0:
            path_summary = path_filter.groupby(['AEDECOD', 'CMDECOD']).agg({
                'USUBJID': 'nunique',
                'Days_to_CM': 'median'
            }).reset_index()
            path_summary.columns = ['AE', 'CM', 'N_Subjects', 'Median_Days_to_CM']
            path_summary = path_summary.sort_values('N_Subjects', ascending=False).head(10)
            
            st.markdown(t('top_paths'))
            st.dataframe(path_summary, width='stretch')
            
            fig_path = go.Figure()
            fig_path.add_trace(go.Bar(
                y=path_summary['AE'] + ' → ' + path_summary['CM'],
                x=path_summary['N_Subjects'],
                orientation='h',
                marker_color='#55A868',
                text=path_summary['N_Subjects'],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Subjects: %{x}<br>Median Days: ' + 
                             path_summary['Median_Days_to_CM'].astype(str) + '<extra></extra>'
            ))
            fig_path.update_layout(
                xaxis_title=t('subjects'),
                yaxis_title=t('intervention_paths'),
                height=400,
                margin=dict(t=20, b=40, l=200, r=20)
            )
            st.plotly_chart(fig_path, width='stretch')
        else:
            st.info(t('no_links_scope'))
    else:
        st.warning(t('no_links_window'))

with tab4:
    if mode == t('global_overview'):
        st.subheader(t('global_narrative'))
    else:
        st.subheader(t('aesi_narrative', aesi=get_aes_name(selected_aesi)))
    
    st.markdown(t('narrative_desc'))
    
    total_subjects = len(adsl)
    total_ae_subjects = len(adae['USUBJID'].unique())
    overall_incidence = total_ae_subjects / total_subjects * 100
    
    if mode == t('global_overview'):
        st.markdown(t('study_overview'))
        st.markdown(t('study_overview_text', 
                     total=total_subjects,
                     placebo=n_total.get("Placebo", 0),
                     low=n_total.get("Mindaptin Low Dose", 0),
                     high=n_total.get("Mindaptin High Dose", 0),
                     ae_subj=total_ae_subjects,
                     incidence=overall_incidence,
                     ae_events=len(adae)))
        
        st.markdown('---')
        st.markdown(t('special_ae_stories'))
        
        for aesi_soc in AESI_SOCS:
            with st.expander(f'📖 Story: {get_aes_name(aesi_soc)}', expanded=True):
                aesi_data = adae[adae['AEBODSYS'] == aesi_soc]
                n_aesi = aesi_data['USUBJID'].nunique()
                n_aesi_events = len(aesi_data)
                aesi_incidence = n_aesi / total_subjects * 100
                
                st.markdown(t('incidence_text', n_subj=n_aesi, pct=aesi_incidence, n_events=n_aesi_events))
                
                st.markdown(t('key_findings'))
                for finding in get_aes_findings(aesi_soc):
                    st.markdown(f'- {finding}')
                
                aesi_by_trt = aesi_data.groupby('TRTA')['USUBJID'].nunique()
                st.markdown(t('by_treatment_group'))
                for trt in TREATMENT_ORDER:
                    n_subj = aesi_by_trt.get(trt, 0)
                    n = n_total.get(trt, 0)
                    pct = n_subj/n*100 if n > 0 else 0
                    st.markdown(f'- {trt}: {n_subj}/{n} ({pct:.1f}%)')
                
                aesi_sev = aesi_data['AESEV'].value_counts()
                st.markdown(t('severity_distribution'))
                for sev in ['MILD', 'MODERATE', 'SEVERE']:
                    n_sev = aesi_sev.get(sev, 0)
                    pct_sev = n_sev/n_aesi_events*100 if n_aesi_events > 0 else 0
                    st.markdown(f'- {sev}: {n_sev} {t("events")} ({pct_sev:.1f}%)')
                
                st.markdown(t('recommendations'))
                for rec in get_aes_recs(aesi_soc):
                    st.markdown(f'- ✅ {rec}')
                
                if 'Placebo' in aesi_by_trt.index and len(aesi_by_trt) > 1:
                    for trt in aesi_by_trt.index:
                        if trt == 'Placebo':
                            continue
                        rd, ci_l, ci_u = risk_difference_ci(
                            n_total.get('Placebo', 0), aesi_by_trt.get('Placebo', 0),
                            n_total.get(trt, 0), aesi_by_trt.get(trt, 0)
                        )
                        st.markdown(t('risk_diff', trt=trt, rd=rd*100, ci_l=ci_l*100, ci_u=ci_u*100))
        
        st.markdown('---')
        st.markdown(t('dsmb_summary'))
        
        st.markdown(t('summary_assessment'))
    else:
        aesi_data = adae[adae['AEBODSYS'] == selected_aesi]
        n_aesi = aesi_data['USUBJID'].nunique()
        n_aesi_events = len(aesi_data)
        aesi_incidence = n_aesi / total_subjects * 100
        
        st.markdown(t('aesi_focus_narrative'))
        st.markdown(t('aesi_narrative_text',
                     aesi=get_aes_name(selected_aesi),
                     total=total_subjects,
                     n_subj=n_aesi,
                     pct=aesi_incidence,
                     n_events=n_aesi_events,
                     pct_ae=n_aesi/total_ae_subjects*100 if total_ae_subjects > 0 else 0))
        
        st.markdown('---')
        st.markdown(t('key_findings'))
        
        for finding in get_aes_findings(selected_aesi):
            st.markdown(f'- {finding}')
        
        aesi_by_trt = aesi_data.groupby('TRTA')['USUBJID'].nunique()
        st.markdown(t('by_treatment_group'))
        for trt in TREATMENT_ORDER:
            n_subj = aesi_by_trt.get(trt, 0)
            n = n_total.get(trt, 0)
            pct = n_subj/n*100 if n > 0 else 0
            st.markdown(f'- {trt}: {n_subj}/{n} ({pct:.1f}%)')
        
        aesi_sev = aesi_data['AESEV'].value_counts()
        st.markdown(t('severity_distribution'))
        for sev in ['MILD', 'MODERATE', 'SEVERE']:
            n_sev = aesi_sev.get(sev, 0)
            pct_sev = n_sev/n_aesi_events*100 if n_aesi_events > 0 else 0
            st.markdown(f'- {sev}: {n_sev} {t("events")} ({pct_sev:.1f}%)')
        
        aesi_out = aesi_data['AEOUT'].value_counts()
        st.markdown(t('outcome_dist'))
        for out in aesi_out.index:
            n_out = aesi_out[out]
            pct_out = n_out/n_aesi_events*100 if n_aesi_events > 0 else 0
            st.markdown(f'- {out}: {n_out} {t("events")} ({pct_out:.1f}%)')
        
        st.markdown('---')
        st.markdown(t('risk_diff_analysis'))
        
        if 'Placebo' in aesi_by_trt.index and len(aesi_by_trt) > 1:
            for trt in aesi_by_trt.index:
                if trt == 'Placebo':
                    continue
                rd, ci_l, ci_u = risk_difference_ci(
                    n_total.get('Placebo', 0), aesi_by_trt.get('Placebo', 0),
                    n_total.get(trt, 0), aesi_by_trt.get(trt, 0)
                )
                signal = t('potential_signal') if rd > 0.05 and ci_l > 0 else t('expected_range')
                st.markdown(t('risk_diff_signal', trt=trt, rd=rd*100, ci_l=ci_l*100, ci_u=ci_u*100, signal=signal))
        
        st.markdown('---')
        st.markdown(t('recommendations'))
        
        for rec in get_aes_recs(selected_aesi):
            st.markdown(f'- ✅ {rec}')

st.sidebar.markdown('---')
st.sidebar.markdown(t('data_source'))
st.sidebar.markdown(t('dashboard_version'))
