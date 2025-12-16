import random
from datetime import datetime, timedelta

class DiscoveryAgent:
    """Mock discovery agent (simulates portal scanning)"""
    
    def __init__(self):
        self.portals = [
            "Government Tender Portal",
            "Industry RFP Platform",
            "Enterprise Customer Portal"
        ]
    
    def simulate_discovery(self):
        """Simulate discovering an RFP"""
        rfp_types = [
            "Cloud Infrastructure Modernization",
            "Enterprise Security Upgrade",
            "Data Center Migration",
            "Digital Transformation Initiative"
        ]
        
        customers = [
            "State Public Sector Unit",
            "Global Bank Corporation", 
            "Healthcare Network Inc",
            "Retail Chain Enterprises"
        ]
        
        return {
            'portal': random.choice(self.portals),
            'rfp_type': random.choice(rfp_types),
            'customer': random.choice(customers),
            'discovered_at': datetime.now().isoformat(),
            'deadline': (datetime.now() + timedelta(days=random.randint(7, 30))).isoformat(),
            'deal_size_tier': random.choice(['Small (<$1M)', 'Medium ($1-5M)', 'Large (>$5M)'])
        }