import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Import our agents
from agents.orchestrator import ChiefOrchestrator
from agents.discovery import DiscoveryAgent
from agents.analyzer import DocumentAnalyzer
from agents.matcher import ProductMatcher
from agents.pricing import PricingAgent

# Page configuration
st.set_page_config(
    page_title="RFP Response Agent",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    div.stButton > button {
        background-color: #FFE600;   /* EY Yellow */
        color: #111827;              /* Dark text for contrast */
        border-radius: 6px;
        padding: 0.55rem 1.4rem;
        font-weight: 600;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #FACC15;   /* Slightly darker EY yellow */
        color: #111827;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem;
    }
    .agent-card {
        border-left: 4px solid #3B82F6;
        padding-left: 1rem;
        margin: 1rem 0;
    }
    .success-badge {
        background-color: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
    }
    .warning-badge {
        background-color: #F59E0B;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'project_data' not in st.session_state:
    st.session_state.project_data = None
if 'workflow_complete' not in st.session_state:
    st.session_state.workflow_complete = False

def main():
    # Header
    st.markdown('<h1 class="main-header"> Enterprise RFP Response Agent</h1>', unsafe_allow_html=True)
    st.markdown("**Multi-Agent AI for B2B RFP Automation - Asian Paints, Tata Capital, Hero, etc.**")
    
    # Sidebar - SHOW ALL OPTIONS AT ONCE
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
        st.markdown("### Navigation")
        
        # Create navigation buttons instead of dropdown
        if st.button("🏠 Dashboard", use_container_width=True, type="primary"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if st.button(" New RFP Analysis", use_container_width=True):
            st.session_state.current_page = "analysis"
            st.rerun()
        
        if st.button(" Results", use_container_width=True):
            st.session_state.current_page = "results"
            st.rerun()
        
        if st.button(" Configuration", use_container_width=True):
            st.session_state.current_page = "configuration"
            st.rerun()
        
        # Initialize current_page if not set
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "dashboard"
        
        st.markdown("---")
        st.markdown("### Status")
        if st.session_state.project_data:
            st.success(f" Project: {st.session_state.project_data.get('project_id', 'N/A')}")
            st.info(f"Confidence: {st.session_state.project_data.get('confidence_score', 0)}%")
        else:
            st.warning("No active project")
        
        st.markdown("---")
        st.markdown("### About")
        st.caption("""
        This MVP demonstrates:
        - Automated RFP analysis
        - Product matching for B2B enterprises
        - Pricing generation (₹ INR)
        - FREE local AI (no API costs)
        """)
    
    # Main content based on menu selection
    if st.session_state.current_page == "dashboard":
        show_dashboard()
    elif st.session_state.current_page == "analysis":
        show_analysis_page()
    elif st.session_state.current_page == "results":
        show_results_page()
    elif st.session_state.current_page == "configuration":
        show_configuration_page()

def show_dashboard():
    """Main dashboard view"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Traditional RFP Time", "5-7 days", "-85%")
    with col2:
        st.metric("Agent RFP Time", "<1 day", "Time saved")
    with col3:
        st.metric("Win Rate Improvement", "+20%", "30% → 50%")
    with col4:
        st.metric("Cost Savings", "₹2L/RFP", "Estimated")
    
    st.markdown("---")
    
    # Agent overview
    st.markdown('<h2 class="sub-header"> Agent Architecture </h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    agents = [
        {"name": "Main Orchestrator", "icon": "👑", "status": "Ready", "color": "#3B82F6", "desc": "Coordinates all agents"},
        {"name": "Sales Agent", "icon": "💰", "status": "Active", "color": "#10B981", "desc": "Discovers RFPs"},
        {"name": "Technical Agent", "icon": "⚙️", "status": "Ready", "color": "#F59E0B", "desc": "Matches specs to SKUs"},
        {"name": "Pricing Agent", "icon": "📊", "status": "Ready", "color": "#8B5CF6", "desc": "Calculates costs"},
        {"name": "Response Compiler", "icon": "📄", "status": "Ready", "color": "#EF4444", "desc": "Generates final bid"}
    ]
    
    for i, agent in enumerate(agents):
        col = [col1, col2, col3, col4, col5][i]
        with col:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; border: 2px solid {agent['color']}; border-radius: 0.5rem;">
                <div style="font-size: 2rem;">{agent['icon']}</div>
                <div style="font-weight: bold; margin: 0.5rem 0;">{agent['name']}</div>
                <div class="success-badge">{agent['status']}</div>
                <div style="font-size: 0.8rem; margin-top: 0.5rem; color: #666;">{agent['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Sample workflow
    st.markdown('<h2 class="sub-header"> Quick Start</h2>', unsafe_allow_html=True)
    
    if st.button(" Run Sample RFP Analysis", type="primary", use_container_width=True):
        with st.spinner("Running automated analysis..."):
            run_sample_analysis()
    
    if st.session_state.project_data:
        st.markdown("---")
        show_project_summary()

def show_analysis_page():
    """Page for analyzing new RFPs"""
    st.markdown('<h2 class="sub-header"> Analyze New RFP</h2>', unsafe_allow_html=True)
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        [" Enter Text", " Upload Document", " Use Sample"]
    )
    
    rfp_text = ""
    customer_name = ""
    rfp_title = ""
    
    if input_method == " Enter Text":
        customer_name = st.text_input("Customer Name", "Asian Paints Ltd")
        rfp_title = st.text_input("RFP Title", "Enterprise Cloud Migration Project")
        rfp_text = st.text_area(
            "Paste RFP Content",
            height=300,
            value="""PROJECT OVERVIEW
Asian Paints Ltd requires modernization of its cloud infrastructure to support digital transformation initiatives across 15 manufacturing plants.

TECHNICAL REQUIREMENTS:
1. The system shall provide 99.95% uptime guarantee with 24/7 monitoring.
2. Must include enterprise support with 2-hour response time for critical issues.
3. Platform must be SOC2 Type II and ISO 27001 certified.
4. Should support auto-scaling based on CPU and memory utilization.
5. Must provide REST API for integration with SAP ERP and Oracle databases.
6. Data encryption at rest (AES-256) and in transit (TLS 1.3) is mandatory.
7. Disaster recovery with RPO < 30 minutes and RTO < 4 hours.
8. Multi-factor authentication for all administrative access.
9. Comprehensive audit logging with 5-year retention.
10. Regular security patching within 48 hours of release.

COMMERCIAL TERMS:
- Payment terms: Net 45 days
- Warranty: Minimum 3 years comprehensive
- Implementation timeline: 6 months phased rollout
- Penalty clauses: 0.1% per day for SLA breaches

COMPLIANCE:
- GDPR compliance for European operations
- ISO27001 certification mandatory
- Industry-specific compliance as applicable"""
        )
    
    elif input_method == " Upload Document":
        uploaded_file = st.file_uploader("Upload RFP Document", type=['pdf', 'docx', 'txt'])
        customer_name = st.text_input("Customer Name", "Asian Paints Ltd")
        rfp_title = st.text_input("RFP Title", "Enterprise Cloud Migration Project")
    
        if uploaded_file is not None:
            # Initialize the parser from your utils
            from utils.document_parser import FreeDocumentParser
            parser = FreeDocumentParser()
        
            # Get file details and read content
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            st.write(f"File uploaded: {file_details['FileName']}")
        
            # Read file content based on type
            bytes_data = uploaded_file.read()
        
            if uploaded_file.name.endswith('.pdf'):
                # Save temporarily to parse
                with open("temp_uploaded_file.pdf", "wb") as f:
                    f.write(bytes_data)
                rfp_text = parser.parse_pdf("temp_uploaded_file.pdf")
            elif uploaded_file.name.endswith('.docx'):
                with open("temp_uploaded_file.docx", "wb") as f:
                    f.write(bytes_data)
                rfp_text = parser.parse_docx("temp_uploaded_file.docx")
            else:  # .txt file
                rfp_text = bytes_data.decode("utf-8")
        
            # Show a preview of the extracted text
            with st.expander("Preview extracted text (first 500 chars)"):
                st.text(rfp_text[:500] + "...")
    
    elif input_method == " Use Sample":
        st.success("Using pre-loaded sample RFP for demonstration")
        rfp_title = "Manufacturing Plant Automation System"
        customer_name = "Hero MotoCorp Ltd"
        rfp_text = """RFP FOR PLANT AUTOMATION SYSTEM - HERO MOTOCORP

PROJECT SCOPE:
Implementation of IoT-enabled automation system across 3 manufacturing plants to improve production efficiency by 25%.

TECHNICAL SPECIFICATIONS:

1. System must support 500+ IoT sensors with real-time data processing
2. Integration with existing SAP ERP system required
3. Real-time dashboard for production monitoring
4. Predictive maintenance capabilities using ML
5. 99.9% system availability during production hours
6. Data backup every 15 minutes with disaster recovery
7. Mobile app for plant managers
8. API for integration with quality control systems
9. User management with role-based access control
10. Compliance with Industry 4.0 standards

COMMERCIAL REQUIREMENTS:
- Budget: ₹8-12 Crores
- Implementation: 9 months
- Warranty: 5 years
- Payment: 30% advance, 40% on delivery, 30% after UAT

COMPLIANCE:
- ISO 9001:2015
- ISO 27001
- Industry 4.0 standards
- Data privacy regulations"""
    
    if rfp_text and customer_name and rfp_title:
        st.markdown("---")
        
        if st.button(" Start Automated Analysis", type="primary", use_container_width=True):
            with st.spinner("Orchestrating agents... This may take a minute."):
                # Create progress bar
                progress_bar = st.progress(0)
                
                # Initialize orchestrator
                orchestrator = ChiefOrchestrator()
                project_id = orchestrator.create_project(rfp_title, customer_name)
                
                # Simulate workflow steps
                for i in range(5):
                    time.sleep(0.5)
                    progress_bar.progress((i + 1) * 20)
                
                # Run orchestration
                project_data = orchestrator.orchestrate_workflow(rfp_text)
                st.session_state.project_data = project_data
                st.session_state.workflow_complete = True
                
                progress_bar.progress(100)
                st.success(f" Analysis complete! Project ID: {project_id}")
                
                # Show immediate results
                show_quick_results(project_data)

def show_quick_results(project_data):
    """Show quick results after analysis"""
    st.markdown("###  Quick Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analysis = project_data.get('workflow_steps', [{}])[1].get('data', {})
        st.metric("Requirements Found", analysis.get('summary', {}).get('requirements_count', 0))
    
    with col2:
        matching = project_data.get('workflow_steps', [{}])[2].get('data', {})
        st.metric("Match Rate", f"{matching.get('match_rate', 0)*100:.1f}%")
    
    with col3:
        pricing = project_data.get('workflow_steps', [{}])[3].get('data', {})
        total_inr = pricing.get('total', 0)
        st.metric("Estimated Total", f"₹{total_inr:,.2f}")
    
    # Show confidence score
    confidence = project_data.get('confidence_score', 0)
    st.progress(confidence/100, f"Confidence Score: {confidence}%")
    
    if confidence < 50:
        st.warning("⚠️ Low confidence - needs human review")
    elif confidence < 75:
        st.info("ℹ️ Moderate confidence - review recommended")
    else:
        st.success("✅ High confidence - ready for submission")
    
    if st.button("View Detailed Results", type="secondary"):
        st.session_state.current_page = "results"
        st.rerun()

def show_results_page():
    """Detailed results page"""
    if not st.session_state.project_data:
        st.warning("No analysis results available. Please run an analysis first.")
        return
    
    project_data = st.session_state.project_data
    
    st.markdown(f'<h2 class="sub-header"> Results: {project_data.get("rfp_title")}</h2>', unsafe_allow_html=True)
    
    # Project info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Project ID:** {project_data.get('project_id')}")
    with col2:
        st.info(f"**Customer:** {project_data.get('customer_name')}")
    with col3:
        confidence = project_data.get('confidence_score', 0)
        if confidence >= 75:
            st.success(f"**Confidence:** {confidence}%")
        elif confidence >= 50:
            st.warning(f"**Confidence:** {confidence}%")
        else:
            st.error(f"**Confidence:** {confidence}%")
    
    # Tabs for different result sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Summary", 
        " Analysis", 
        " Matching", 
        " Pricing", 
        " Final Response"
    ])
    
    with tab1:
        show_summary_tab(project_data)
    
    with tab2:
        show_analysis_tab(project_data)
    
    with tab3:
        show_matching_tab(project_data)
    
    with tab4:
        show_pricing_tab(project_data)
    
    with tab5:
        show_response_tab(project_data)

def show_summary_tab(project_data):
    """Summary tab content"""
    st.markdown("### Workflow Summary")
    
    # Timeline visualization
    steps = project_data.get('workflow_steps', [])
    
    for step in steps:
        with st.expander(f" {step['step'].upper()}", expanded=True):
            if step['step'] == 'discovery':
                data = step['data']
                st.json(data)
            elif step['step'] == 'analysis':
                data = step['data']
                st.metric("Requirements Identified", data.get('summary', {}).get('requirements_count', 0))
                st.write("**Key Terms:**", ", ".join(data.get('summary', {}).get('key_terms', [])))
            elif step['step'] == 'matching':
                data = step['data']
                st.metric("Match Rate", f"{data.get('match_rate', 0)*100:.1f}%")
            elif step['step'] == 'pricing':
                data = step['data']
                total_inr = data.get('total', 0)
                st.metric("Total Proposal Value", f"₹{total_inr:,.2f}")
    
    # Confidence gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=project_data.get('confidence_score', 0),
        title={'text': "Confidence Score"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "green"}
            ]
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def show_analysis_tab(project_data):
    """Analysis tab content"""
    analysis_data = project_data.get('workflow_steps', [{}])[1].get('data', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("####  Requirements by Category")
        categorized = analysis_data.get('categorized_requirements', {})
        
        categories = list(categorized.keys())
        counts = [len(categorized[cat]) for cat in categories]
        
        fig = go.Figure(data=[go.Pie(labels=categories, values=counts)])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("####  Compliance Requirements")
        compliance = analysis_data.get('compliance_requirements', [])
        if compliance:
            for item in compliance:
                st.success(f" {item}")
        else:
            st.info("No specific compliance requirements identified")
    
    st.markdown("####  Extracted Requirements")
    requirements = analysis_data.get('requirements', [])
    if requirements:
        df = pd.DataFrame(requirements)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No requirements extracted")

def show_matching_tab(project_data):
    """Matching tab content"""
    matching_data = project_data.get('workflow_steps', [{}])[2].get('data', {})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("####  Matched Products")
        matched = matching_data.get('matched_products', [])
        if matched:
            df_matched = pd.DataFrame(matched)
            st.dataframe(df_matched[['requirement_id', 'matched_product', 'confidence', 'similarity_score']], 
                        use_container_width=True)
        else:
            st.info("No products matched")
    
    with col2:
        st.markdown("####  Match Metrics")
        st.metric("Overall Match Rate", f"{matching_data.get('match_rate', 0)*100:.1f}%")
        st.metric("Requirements", matching_data.get('total_requirements', 0))
        st.metric("Matched", matching_data.get('matched_requirements', 0))
        st.metric("Gaps", len(matching_data.get('gaps', [])))
        
        st.markdown("####  Recommended Bundle")
        st.success(matching_data.get('recommended_bundle', 'N/A'))
    
    st.markdown("#### ⚠️ Identified Gaps")
    gaps = matching_data.get('gaps', [])
    if gaps:
        for gap in gaps:
            st.warning(f"**{gap['requirement_id']}**: {gap['requirement_text'][:100]}...")
            st.caption(f"Reason: {gap.get('gap_reason', 'Unknown')}")
    else:
        st.success("No significant gaps identified!")

def show_pricing_tab(project_data):
    """Pricing tab content"""
    pricing_data = project_data.get('workflow_steps', [{}])[3].get('data', {})
    
    # Pricing summary
    col1, col2, col3 = st.columns(3)
    with col1:
        subtotal_inr = pricing_data.get('subtotal', 0)
        st.metric("Subtotal", f"₹{subtotal_inr:,.2f}")
    with col2:
        discount_inr = pricing_data.get('discounts', [{}])[0].get('amount', 0)
        st.metric("Discount", f"-₹{discount_inr:,.2f}")
    with col3:
        total_inr = pricing_data.get('total', 0)
        st.metric("**Total**", f"₹{total_inr:,.2f}")
    
    st.markdown("####  Line Items (₹ INR)")
    line_items = pricing_data.get('line_items', [])
    if line_items:
        df_items = pd.DataFrame(line_items)
        df_items['unit_price'] = df_items['unit_price'].map(lambda x: f'₹{x:,.2f}')
        df_items['extended_price'] = df_items['extended_price'].map(lambda x: f'₹{x:,.2f}')
        st.dataframe(df_items, use_container_width=True)
    
    st.markdown("####  Pricing Details")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Payment Terms:** {pricing_data.get('payment_terms', 'N/A')}")
        st.info(f"**Validity:** {pricing_data.get('validity', 'N/A')}")
    
    with col2:
        positioning = pricing_data.get('competitive_positioning', 'N/A')
        st.success(f"**Competitive Positioning:** {positioning}")
        st.success(f"**Customer Tier:** {pricing_data.get('customer_tier', 'N/A').upper()}")
    
    # Discount breakdown in INR
    st.markdown("####  Discount Breakdown (₹)")
    discounts = pricing_data.get('discounts', [])
    for discount in discounts:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**{discount.get('type', 'Discount')}**")
        with col2:
            st.write(f"{discount.get('percent', 0)}%")
        with col3:
            discount_amount_inr = discount.get('amount', 0)
            st.write(f"₹{discount_amount_inr:,.2f}")

def show_response_tab(project_data):
    """Final response tab"""
    st.markdown("####  Generated RFP Response (Ready for Submission)")
    
    # Generate response text
    response_text = generate_response_text(project_data)
    
    # Display in expandable text area
    with st.expander("View Full Response", expanded=True):
        st.text_area("Generated Response", response_text, height=400)
    
    # Download buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(" Download as DOCX", use_container_width=True):
            st.success("DOCX download would be implemented here")
    with col2:
        if st.button(" Download as PDF", use_container_width=True):
            st.success("PDF generation would be implemented here")
    with col3:
        if st.button(" Copy to Clipboard", use_container_width=True):
            st.success("Response copied to clipboard")

def generate_response_text(project_data):
    """Generate final response text"""
    rfp_title = project_data.get('rfp_title', 'RFP Response')
    customer = project_data.get('customer_name', 'Customer')
    
    analysis_data = project_data.get('workflow_steps', [{}])[1].get('data', {})
    matching_data = project_data.get('workflow_steps', [{}])[2].get('data', {})
    pricing_data = project_data.get('workflow_steps', [{}])[3].get('data', {})
    
    response = f"""
PROPOSAL FOR: {rfp_title}
PROPOSAL BY: TechCorp Solutions India Pvt. Ltd.
DATE: {datetime.now().strftime('%B %d, %Y')}
REF: {project_data.get('project_id', 'RFP-001')}

EXECUTIVE SUMMARY
Thank you for the opportunity to respond to your RFP. Our solution addresses 
{analysis_data.get('summary', {}).get('requirements_count', 0)} requirements 
identified in your RFP with a {matching_data.get('match_rate', 0)*100:.1f}% match rate 
to our existing product catalog.

TECHNICAL RESPONSE
─────────────────────────────────────────────────────
Based on our analysis, we recommend our {matching_data.get('recommended_bundle', 'Enterprise Bundle')}.
Key capabilities include:

{matching_data.get('matched_requirements', 0)} out of {matching_data.get('total_requirements', 0)} 
requirements are fully addressed by our standard products.

PRICING PROPOSAL (INDIAN RUPEES)
─────────────────────────────────────────────────────
"""
    
    # Add pricing details in INR
    line_items = pricing_data.get('line_items', [])
    for item in line_items:
        price_inr = item['extended_price']
        response += f"{item['name']} ({item['quantity']} units): ₹{price_inr:,.2f}\n"
    
    subtotal_inr = pricing_data.get('subtotal', 0)
    discount_inr = pricing_data.get('discounts', [{}])[0].get('amount', 0)
    total_inr = pricing_data.get('total', 0)
    
    response += f"""
─────────────────────────────────────────────────────
SUBTOTAL: ₹{subtotal_inr:,.2f}
DISCOUNTS: -₹{discount_inr:,.2f}
─────────────────────────────────────────────────────
TOTAL PROPOSED: ₹{total_inr:,.2f}
(Valid for {pricing_data.get('validity', '90 days')})

COMPETITIVE POSITIONING
{pricing_data.get('competitive_positioning', 'Competitively priced solution')}

NEXT STEPS
We recommend a technical deep-dive session to address the {len(matching_data.get('gaps', []))} 
identified gaps and finalize the solution architecture.

Sincerely,
TechCorp Solutions India Team
"""
    
    return response

def show_configuration_page():
    """Configuration page"""
    st.markdown('<h2 class="sub-header"> Configuration</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Product Catalog", "Pricing Rules", "Agent Settings"])
    
    with tab1:
        st.markdown("#### Product Catalog")
        with open("data/product_catalog.json", "r") as f:
            catalog = json.load(f)
        
        st.json(catalog)
        
        if st.button("Reload Catalog", type="secondary"):
            st.success("Catalog reloaded")
    
    with tab2:
        st.markdown("#### Pricing Rules (INR)")
        
        # Display current rules
        pricing_agent = PricingAgent()
        rules = pricing_agent.rules
        st.json(rules)
        
        # Simple rule editor
        st.markdown("##### Edit Volume Discounts")
        col1, col2 = st.columns(2)
        with col1:
            min_units = st.number_input("Minimum Units", min_value=1, value=10)
        with col2:
            discount = st.number_input("Discount %", min_value=0, max_value=100, value=5)
        
        if st.button("Add Discount Rule", type="secondary"):
            st.success(f"Added: {min_units} units → {discount}% discount")
    
    with tab3:
        st.markdown("#### Agent Settings")
        
        # Confidence thresholds
        st.markdown("##### Confidence Thresholds")
        high_threshold = st.slider("High Confidence", 70, 95, 75)
        medium_threshold = st.slider("Medium Confidence", 50, 85, 50)
        
        st.info(f"Settings will take effect on next analysis")
        
        # Reset button
        if st.button("Reset to Defaults", type="secondary"):
            st.success("Settings reset to defaults")

def run_sample_analysis():
    """Run a sample analysis for dashboard demo"""
    # Create sample data
    sample_text = """SAMPLE RFP: Manufacturing Plant IoT System
    
    REQUIREMENTS:
    1. Must support 500+ IoT sensors with real-time monitoring
    2. Integration with SAP ERP system required
    3. Predictive maintenance using machine learning
    4. 99.9% system availability during production
    5. Mobile app for plant managers
    
    COMMERCIAL:
    - Budget: ₹5-8 Crores
    - Timeline: 6 months implementation
    - Warranty: 4 years"""
    
    orchestrator = ChiefOrchestrator()
    project_id = orchestrator.create_project(
        "Manufacturing Plant IoT System", 
        "Sample Manufacturing Company"
    )
    
    project_data = orchestrator.orchestrate_workflow(sample_text)
    st.session_state.project_data = project_data
    st.session_state.workflow_complete = True
    
    st.success(f"Sample analysis complete! Confidence: {project_data.get('confidence_score')}%")

def show_project_summary():
    """Show project summary in dashboard"""
    project_data = st.session_state.project_data
    
    st.markdown("###  Latest Project Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analysis = project_data.get('workflow_steps', [{}])[1].get('data', {})
        st.metric("Requirements", analysis.get('summary', {}).get('requirements_count', 0))
    
    with col2:
        matching = project_data.get('workflow_steps', [{}])[2].get('data', {})
        st.metric("Match Rate", f"{matching.get('match_rate', 0)*100:.1f}%")
    
    with col3:
        pricing = project_data.get('workflow_steps', [{}])[3].get('data', {})
        total_inr = pricing.get('total', 0)
        st.metric("Total Value", f"₹{total_inr:,.2f}")
    
    if st.button("View Full Results", type="primary"):
        st.session_state.current_page = "results"
        st.rerun()

if __name__ == "__main__":
    main()




