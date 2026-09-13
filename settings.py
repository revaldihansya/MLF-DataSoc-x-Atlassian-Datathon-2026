"""Explicit analytical choices. Edit these, not the raw CSVs."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent
FILES = {'customers': 'customers.csv', 'tickets': 'customer_support_tickets.csv', 'usage': 'product_usage.csv'}
BASELINE_MONTHS = ['2023-01', '2023-02']
RECENT_MONTHS = ['2023-04', '2023-05']
EARLIER_MONTHS = ['2023-03', '2023-04']
DECLINE_THRESHOLD = -0.20
MIN_DISPLAY_N = 30  # Display warning, not a universal statistical rule.
USAGE_METRICS = ['active_days', 'sessions', 'product_actions', 'collaborators', 'integrations_used']
CATEGORICAL_PREDICTORS = ['product', 'ticket_type', 'ticket_subject', 'ticket_priority', 'ticket_channel', 'plan_type', 'industry', 'region', 'company_size']
VOCABULARY = {
 'product': ['Jira','Confluence','Trello','Bitbucket','Loom'],
 'product_purchased': ['Jira','Confluence','Trello','Bitbucket','Loom'],
 'ticket_status': ['Closed','Open','Pending Customer Response'],
 'ticket_priority': ['Low','Medium','High','Critical'],
 'ticket_type': ['Refund request','Cancellation request','Technical issue','Product inquiry','Billing inquiry'],
 'ticket_channel': ['Email','Phone','Social media','Chat'],
 'plan_type': ['Free','Standard','Premium','Enterprise'],
 'ticket_subject': ['Refund request','Software bug','Product compatibility','Email delivery problem','Device compatibility issue','Loading issue','Network problem','Installation support','Product setup','Payment issue','Product recommendation','Account access','Integration','Data loss','Cancellation request','Display issue']}
# These are analytical groupings, not source ground truth or verified product defects.
TECHNICAL_SUBJECTS = ['Software bug','Product compatibility','Device compatibility issue','Loading issue','Network problem','Installation support','Product setup','Integration','Data loss','Display issue']
