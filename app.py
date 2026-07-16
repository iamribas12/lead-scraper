import streamlit as st
import asyncio
import pandas as pd
import re
from engine import PlaywrightMapsEngine

from utils import generate_excel

st.set_page_config(page_title="High-Speed Playwright Scraper", layout="wide", page_icon="📍")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1300px; padding-top: 2rem; padding-bottom: 2rem; }
    h1 { font-size: 1.8rem; color: #2c3e50; margin-bottom: 0px; }
    .stDataFrame { font-size: 0.85rem; }
    .stButton>button { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Advanced Free Filtering")
    filter_email = st.checkbox("Email Address", value=False)
    filter_phone = st.checkbox("Contact number", value=False)

st.title("📍 High-Speed Playwright Maps Scraper")
st.markdown("Extracts data directly from the sidebar. High-Speed parallel scraping with Stealth Jitter. **100% Free.**")
st.markdown("---")

def passes_filters(lead):
    has_email = bool(lead.get('Email Address', '').strip())
    has_phone = bool(lead.get('Contact Number', '').strip())
    
    if filter_email and not has_email:
        return False
    if filter_phone and not has_phone:
        return False
        
    return True

with st.container():
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_query = st.text_input("Search Query", placeholder="E.g., Plumbers in Manchester")
    with col2:
        lead_limit = st.slider("Target Lead Limit", min_value=1, max_value=500, value=20, step=5)
    with col3:
        headless = st.checkbox("Headless Mode", value=True, help="Hide the browser.")

    trigger = st.button("🚀 Start Search & Extraction", type="primary", use_container_width=True)
    st.markdown("---")

    async def execute_scraping(ctx):
        if not search_query:
            st.error("Please enter a search query.")
            return
            
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        table_placeholder = st.empty()
        download_placeholder = st.empty()
        
        st.markdown("### 🖥️ Live Activity Console")
        log_container = st.container()
        with log_container:
            log_placeholder = st.empty()
            
        log_messages = []
        def ui_log(msg):
            log_messages.append(msg)
            display_logs = "\n".join(log_messages[-15:])
            log_placeholder.code(display_logs, language="bash")

        scraper = PlaywrightMapsEngine(search_query, lead_limit, headless, ctx=ctx, log_callback=ui_log)
        leads = []
        filtered_leads = []
        
        try:
            async for yielded_count, total, lead in scraper.run_generator():
                progress = float(yielded_count / total) if total > 0 else 0.0
                progress_bar.progress(progress)
                
                status_text.info(f"Gathering ({yielded_count}/{total}): **{lead.get('Business Name', '')}**")
                
                leads.append(lead)
                
                if passes_filters(lead):
                    filtered_leads.append(lead)
                
                if filtered_leads:
                    df = pd.DataFrame(filtered_leads)
                    table_placeholder.dataframe(
                        df,
                        column_config={
                            "Website URL": st.column_config.LinkColumn("Website URL")
                        },
                        hide_index=True
                    )
                    
            status_text.success(f"✅ Scraping complete. Total Leads: {len(leads)}, Passed Filters: {len(filtered_leads)}")
            progress_bar.progress(1.0)
            
            if len(filtered_leads) >= 1:
                df = pd.DataFrame(filtered_leads)
                excel_bytes = generate_excel(df)
                csv_bytes = df.to_csv(index=False).encode('utf-8')
                
                with download_placeholder.container():
                    colA, colB = st.columns(2)
                    with colA:
                        st.download_button(
                            label=f"📥 Export to Excel (.xlsx)",
                            data=excel_bytes,
                            file_name=f"google_maps_leads.xlsx",
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            type="primary",
                            use_container_width=True
                        )
                    with colB:
                        st.download_button(
                            label=f"📥 Export to CSV (.csv)",
                            data=csv_bytes,
                            file_name=f"google_maps_leads.csv",
                            mime='text/csv',
                            type="primary",
                            use_container_width=True
                        )
            else:
                st.warning("No leads found matching your criteria.")
                    
        except Exception as e:
            import traceback
            st.error(f"Execution Error: {e}")
            st.code(traceback.format_exc(), language="python")

    from streamlit.runtime.scriptrunner import get_script_run_ctx

    if trigger:
        ctx = get_script_run_ctx()
        asyncio.run(execute_scraping(ctx))
