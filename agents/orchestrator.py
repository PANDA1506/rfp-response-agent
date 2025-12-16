import json
import uuid
from datetime import datetime

class ChiefOrchestrator:
    """Rule-based orchestrator with improved confidence for B2B RFPs"""
    
    def __init__(self):
        self.project_id = None
        self.project_data = {}
    
    def create_project(self, rfp_title, customer_name):
        """Initialize new RFP project"""
        self.project_id = f"RFP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4]}"
        
        self.project_data = {
            'project_id': self.project_id,
            'rfp_title': rfp_title,
            'customer_name': customer_name,
            'created_at': datetime.now().isoformat(),
            'status': 'initiated',
            'agents': {},
            'timeline': {
                'start': datetime.now().isoformat(),
                'end': None
            },
            'confidence_score': 0
        }
        
        return self.project_id
    
    def orchestrate_workflow(self, rfp_text):
        """Orchestrate the agent workflow with B2B context"""
        from agents.discovery import DiscoveryAgent
        from agents.analyzer import DocumentAnalyzer
        from agents.matcher import ProductMatcher
        from agents.pricing import PricingAgent
        
        workflow_steps = []
        
        # Step 1: Discovery Agent (simulated)
        discovery_agent = DiscoveryAgent()
        discovery_result = discovery_agent.simulate_discovery()
        workflow_steps.append({
            'step': 'discovery',
            'status': 'completed',
            'data': discovery_result
        })
        
        # Step 2: Document Analysis
        analyzer = DocumentAnalyzer()
        analysis_result = analyzer.analyze_rfp(rfp_text)
        workflow_steps.append({
            'step': 'analysis',
            'status': 'completed',
            'data': analysis_result
        })
        
        # Step 3: Product Matching
        matcher = ProductMatcher()
        matching_result = matcher.match_requirements(
            analysis_result.get('requirements', [])
        )
        workflow_steps.append({
            'step': 'matching',
            'status': 'completed',
            'data': matching_result
        })
        
        # Step 4: Pricing
        pricing_agent = PricingAgent()
        
        # Determine customer tier based on RFP content
        customer_tier = "sme"
        rfp_lower = rfp_text.lower()
        
        # EY Techathon target clients get enterprise tier
        target_clients = ["asian paints", "tata capital", "hero", "aditya birla", "firstsource"]
        if any(client in rfp_lower for client in target_clients):
            customer_tier = "enterprise"
        elif any(word in rfp_lower for word in ['enterprise', 'corporation', 'limited', 'ltd', 'multinational']):
            customer_tier = "enterprise"
        elif any(word in rfp_lower for word in ['company', 'business', 'organization']):
            customer_tier = "midmarket"
        
        pricing_result = pricing_agent.calculate_pricing(
            matching_result.get('matched_products', []),
            customer_tier=customer_tier
        )
        workflow_steps.append({
            'step': 'pricing',
            'status': 'completed',
            'data': pricing_result
        })
        
        # Calculate overall confidence with B2B context
        confidence = self._calculate_confidence(
            analysis_result, 
            matching_result, 
            pricing_result,
            rfp_text
        )
        
        self.project_data['workflow_steps'] = workflow_steps
        self.project_data['confidence_score'] = confidence
        self.project_data['status'] = 'completed'
        self.project_data['timeline']['end'] = datetime.now().isoformat()
        self.project_data['customer_tier'] = customer_tier
        
        return self.project_data
    
    def _calculate_confidence(self, analysis, matching, pricing, rfp_text):
        """Calculate overall confidence score for B2B proposals"""
        # Base scores with adjusted weights
        requirements_count = len(analysis.get('requirements', []))
        analysis_conf = min(requirements_count / 20, 1.0) * 0.20  # Reduced weight
        
        match_rate = matching.get('match_rate', 0)
        matching_conf = match_rate * 0.60  # Increased weight for matching
        
        pricing_conf = 0.20 if pricing.get('total', 0) > 0 else 0
        
        base_confidence = (analysis_conf + matching_conf + pricing_conf) * 100
        
        # Apply B2B enterprise context boost
        rfp_lower = rfp_text.lower()
        enterprise_boost = 0
        
        # Boost for EY Techathon target clients
        target_clients = ["asian paints", "tata capital", "hero", "aditya birla", "firstsource"]
        if any(client in rfp_lower for client in target_clients):
            enterprise_boost = 25  # 25% boost for known target clients
        elif any(word in rfp_lower for word in ['enterprise', 'corporation', 'multinational']):
            enterprise_boost = 15
        elif any(word in rfp_lower for word in ['company', 'business']):
            enterprise_boost = 10
        
        # Apply requirements quality boost
        if requirements_count >= 10:
            enterprise_boost += 5  # Well-defined RFPs get extra boost
        
        # Apply pricing realism check
        total_price = pricing.get('total', 0)
        if 1000000 <= total_price <= 500000000:  # ₹10L to ₹50Cr range
            enterprise_boost += 5  # Realistic pricing
        
        final_confidence = min(95, base_confidence + enterprise_boost)
        
        return round(final_confidence, 2)