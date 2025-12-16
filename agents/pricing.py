import json
import random

class PricingAgent:
    """Rule-based pricing engine for B2B enterprises in Indian Rupees"""
    
    def __init__(self, catalog_path="data/product_catalog.json"):
        with open(catalog_path, 'r') as f:
            self.catalog = json.load(f)
        
        # Pricing rules in INR for B2B enterprises
        self.rules = {
            'volume_discount': [
                {'min_units': 5, 'discount': 10},
                {'min_units': 20, 'discount': 20},
                {'min_units': 50, 'discount': 30}
            ],
            'customer_tier_discount': {
                'enterprise': 15,      # Large corporations
                'midmarket': 10,       # Medium businesses
                'sme': 5              # Small businesses
            },
            'services_rate': 25000,    # ₹25,000 per hour for enterprise consulting
            'maintenance_rate': 0.18,  # 18% of hardware/software for annual maintenance
            'implementation_multiplier': 0.25  # 25% of product cost for implementation
        }
    
    def calculate_pricing(self, matched_products, customer_tier="enterprise"):
        """Calculate pricing for matched products in INR"""
        line_items = []
        subtotal = 0
        
        # Group products by SKU to calculate quantities
        product_quantities = {}
        for match in matched_products:
            sku = match['matched_sku']
            product_quantities[sku] = product_quantities.get(sku, 0) + 1
        
        # Calculate pricing for each product
        for sku, quantity in product_quantities.items():
            product = self._get_product_by_sku(sku)
            if product:
                base_price = product['base_price']
                
                # Apply volume discount
                discount = self._calculate_volume_discount(quantity)
                discounted_price = base_price * (1 - discount/100)
                extended_price = discounted_price * quantity
                
                line_items.append({
                    'sku': sku,
                    'name': product['name'],
                    'quantity': quantity,
                    'unit_price': round(discounted_price, 2),
                    'discount_percent': discount,
                    'extended_price': round(extended_price, 2),
                    'category': product['category']
                })
                
                subtotal += extended_price
        
        # Add implementation services (25% of product cost)
        implementation_cost = subtotal * self.rules['implementation_multiplier']
        implementation_hours = int(implementation_cost / self.rules['services_rate'])
        
        line_items.append({
            'sku': 'SERV-IMP',
            'name': 'Implementation & Deployment Services',
            'quantity': implementation_hours,
            'unit_price': self.rules['services_rate'],
            'discount_percent': 0,
            'extended_price': round(implementation_cost, 2),
            'category': 'Services'
        })
        
        subtotal += implementation_cost
        
        # Add annual maintenance (18% of total)
        maintenance_cost = subtotal * self.rules['maintenance_rate']
        line_items.append({
            'sku': 'MAINT-ANNUAL',
            'name': 'Annual Maintenance & Support (First Year)',
            'quantity': 1,
            'unit_price': maintenance_cost,
            'discount_percent': 0,
            'extended_price': round(maintenance_cost, 2),
            'category': 'Support'
        })
        
        subtotal += maintenance_cost
        
        # Add training (fixed 50 hours for enterprise)
        training_cost = 50 * self.rules['services_rate'] * 0.7  # 30% discount on training
        line_items.append({
            'sku': 'TRAIN-ENTERPRISE',
            'name': 'Enterprise User Training (50 hours)',
            'quantity': 1,
            'unit_price': training_cost,
            'discount_percent': 0,
            'extended_price': round(training_cost, 2),
            'category': 'Training'
        })
        
        subtotal += training_cost
        
        # Apply customer tier discount
        customer_discount = self.rules['customer_tier_discount'].get(customer_tier, 0)
        discount_amount = subtotal * (customer_discount / 100)
        total = subtotal - discount_amount
        
        # Determine payment terms based on total
        if total > 10000000:  # Over 1 crore
            payment_terms = '30% advance, 40% on delivery, 30% after UAT'
        elif total > 5000000:  # Over 50 lakhs
            payment_terms = '40% advance, 60% on delivery'
        else:
            payment_terms = '50% advance, 50% on delivery'
        
        return {
            'line_items': line_items,
            'subtotal': round(subtotal, 2),
            'discounts': [
                {
                    'type': f'{customer_tier.capitalize()} Discount',
                    'percent': customer_discount,
                    'amount': round(discount_amount, 2)
                }
            ],
            'total': round(total, 2),
            'payment_terms': payment_terms,
            'validity': '90 days from proposal date',
            'competitive_positioning': self._get_competitive_positioning(total),
            'customer_tier': customer_tier
        }
    
    def _get_product_by_sku(self, sku):
        """Get product by SKU"""
        for product in self.catalog['products']:
            if product['sku'] == sku:
                return product
        return None
    
    def _calculate_volume_discount(self, quantity):
        """Calculate volume discount based on quantity"""
        for rule in sorted(self.rules['volume_discount'], key=lambda x: x['min_units'], reverse=True):
            if quantity >= rule['min_units']:
                return rule['discount']
        return 0
    
    def _get_competitive_positioning(self, total_price):
        """Generate competitive positioning statement for B2B market"""
        # Market positioning based on price range
        if total_price > 50000000:  # Over 5 crores
            return "Premium enterprise solution with comprehensive support and customization"
        elif total_price > 10000000:  # 1-5 crores
            return "Competitively priced for large enterprise deployments with strong ROI"
        elif total_price > 5000000:  # 50 lakhs - 1 crore
            return "Value-optimized solution balancing features and cost for mid-market"
        else:
            return "Cost-effective solution for SME digital transformation"