import re
from utils.document_parser import FreeDocumentParser

class DocumentAnalyzer:
    """SIMPLIFIED analyzer that works with any RFP format"""
    
    def __init__(self):
        self.parser = FreeDocumentParser()
        
    def analyze_rfp(self, text):
        """Analyze RFP text - WORKING VERSION"""
        
        # Extract requirements (using improved parser)
        requirements = self.parser.extract_requirements(text)
        
        # If parser returns empty, create basic requirements
        if not requirements:
            requirements = self._create_basic_requirements(text)
        
        # Extract sections
        sections = self.parser.extract_sections(text)
        
        # Simple analysis
        word_count = len(text.split())
        
        # Extract budget info
        budget = self._extract_budget(text)
        
        # Count requirements by scanning text
        req_count = len(requirements)
        
        return {
            'summary': {
                'word_count': word_count,
                'estimated_pages': max(1, word_count // 500),
                'requirements_count': req_count,
                'budget_mentioned': budget,
                'simple_analysis': True
            },
            'requirements': requirements,
            'sections': sections,
            'categorized_requirements': self._simple_categorize(requirements),
            'compliance_requirements': self._simple_compliance(text)
        }
    
    def _create_basic_requirements(self, text):
        """Create basic requirements from text"""
        requirements = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Take meaningful lines as requirements
        for i, line in enumerate(lines[:15]):  # First 15 non-empty lines
            if len(line) > 15 and not line.startswith('RFP') and not line.startswith('COMPANY'):
                requirements.append({
                    'text': line,
                    'page': 1,
                    'priority': 'Mandatory' if i < 5 else 'Desirable',
                    'type': 'technical'
                })
        
        return requirements
    
    def _simple_categorize(self, requirements):
        """Simple categorization"""
        categories = {
            'technical': [],
            'security': [],
            'commercial': [],
            'support': []
        }
        
        for req in requirements:
            text_lower = req['text'].lower()
            
            if any(word in text_lower for word in ['price', 'cost', 'budget', 'payment']):
                categories['commercial'].append(req)
            elif any(word in text_lower for word in ['security', 'encrypt', 'access', 'auth']):
                categories['security'].append(req)
            elif any(word in text_lower for word in ['support', 'help', 'maintenance']):
                categories['support'].append(req)
            else:
                categories['technical'].append(req)
        
        return categories
    
    def _simple_compliance(self, text):
        """Simple compliance extraction"""
        text_lower = text.lower()
        compliance = []
        
        standards = ['iso', 'gdpr', 'soc2', 'hipaa', 'pci', 'industry', 'compliance']
        for standard in standards:
            if standard in text_lower:
                compliance.append(standard.upper())
        
        return compliance
    
    def _extract_budget(self, text):
        """Extract budget information"""
        # Look for budget mentions
        budget_patterns = [
            r'budget[:\s]*[\$₹]?\s*(\d[\d,\.]+\s*(lakhs?|crores?|lacs?|million|cr))',
            r'[\$₹]\s*(\d[\d,\.]+)\s*(lakhs?|crores?|lacs?|million|cr)',
            r'(\d[\d,\.]+)\s*(lakhs?|crores?|lacs?|million|cr)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Not specified"