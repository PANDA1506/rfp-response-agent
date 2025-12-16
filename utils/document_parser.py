import re
import PyPDF2
from docx import Document
import fitz  # PyMuPDF

class FreeDocumentParser:
    """IMPROVED document parser for RFP analysis"""
    
    def parse_pdf(self, file_path):
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except:
            # Fallback to PyMuPDF
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
        return text
    
    def parse_docx(self, file_path):
        """Extract text from DOCX"""
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    def extract_requirements(self, text):
        """FIXED: Better requirement extraction for all RFP formats"""
        requirements = []
        
        # Clean and prepare text
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        lines = text.split('\n')
        
        requirement_counter = 1
        
        # Look for numbered requirements (1., 2., etc.)
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Pattern 1: Numbered requirements (1., 2., 3., etc.)
            numbered_match = re.match(r'^(\d+)[\.\)]\s+(.+)', line)
            if numbered_match and len(line) > 10:
                req_text = numbered_match.group(2).strip()
                if len(req_text) > 15:  # Avoid very short lines
                    requirements.append({
                        'text': req_text,
                        'page': 1,
                        'priority': 'Mandatory',
                        'type': 'technical'
                    })
                    requirement_counter += 1
                    continue
            
            # Pattern 2: Bullet points with dashes
            if line.startswith('- ') and len(line) > 10:
                req_text = line[2:].strip()
                requirements.append({
                    'text': req_text,
                    'page': 1,
                    'priority': 'Desirable',
                    'type': 'technical'
                })
                requirement_counter += 1
                continue
            
            # Pattern 3: Lines with "need", "must", "should", "require"
            lower_line = line.lower()
            requirement_keywords = ['need', 'must', 'should', 'require', 'shall', 'has to']
            if any(keyword in lower_line for keyword in requirement_keywords):
                requirements.append({
                    'text': line,
                    'page': 1,
                    'priority': 'Mandatory' if 'must' in lower_line or 'shall' in lower_line else 'Desirable',
                    'type': 'technical'
                })
                requirement_counter += 1
                continue
            
            # Pattern 4: Any line that looks like a requirement (contains verbs)
            if len(line) > 20 and len(line.split()) > 4:
                # Check if it's a requirement-like sentence
                verbs = ['support', 'provide', 'include', 'have', 'be', 'do', 'work', 'integrate']
                if any(verb in lower_line for verb in verbs):
                    requirements.append({
                        'text': line,
                        'page': 1,
                        'priority': 'Optional',
                        'type': 'technical'
                    })
                    requirement_counter += 1
        
        # If we found very few requirements, use sentence-based extraction
        if len(requirements) < 3:
            return self._extract_by_sentences(text)
        
        return requirements
    
    def _extract_by_sentences(self, text):
        """Fallback: Extract requirements by sentences"""
        requirements = []
        
        # Split by sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        requirement_keywords = [
            'must', 'shall', 'should', 'need', 'require',
            'support', 'provide', 'include', 'have', 'ensure',
            'capable of', 'able to', 'comply with', 'meet'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            
            lower_sentence = sentence.lower()
            
            # Check if this looks like a requirement
            if any(keyword in lower_sentence for keyword in requirement_keywords):
                requirements.append({
                    'text': sentence,
                    'page': 1,
                    'priority': 'Mandatory' if 'must' in lower_sentence or 'shall' in lower_sentence else 'Desirable',
                    'type': 'technical'
                })
        
        # If still no requirements, take key sentences
        if len(requirements) < 2:
            sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
            for i, sentence in enumerate(sentences[:10]):  # Take first 10 meaningful sentences
                requirements.append({
                    'text': sentence,
                    'page': 1,
                    'priority': 'Optional',
                    'type': 'technical'
                })
        
        return requirements
    
    def _estimate_page(self, text, position):
        """Estimate page number"""
        chars_per_page = 3000
        return (position // chars_per_page) + 1
    
    def extract_sections(self, text):
        """Extract common RFP sections - SIMPLIFIED"""
        sections = {
            'technical': '',
            'commercial': '',
            'compliance': '',
            'general': ''
        }
        
        # Look for section headers
        lines = text.split('\n')
        current_section = 'general'
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(word in line_lower for word in ['technical', 'specification', 'requirement']):
                current_section = 'technical'
            elif any(word in line_lower for word in ['commercial', 'price', 'cost', 'budget', 'payment']):
                current_section = 'commercial'
            elif any(word in line_lower for word in ['compliance', 'certification', 'standard']):
                current_section = 'compliance'
            
            if line.strip():
                sections[current_section] += line + '\n'
        
        return sections