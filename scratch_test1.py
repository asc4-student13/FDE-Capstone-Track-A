# scratch_test.py: delete before Session 4
from agent import recommend_procurement_action
from models import PurchaseRequest

# REQ-001: straightforward approve
req = PurchaseRequest(
    request_id="REQ-001",
    requestor="j.smith@fedex.com",
    cost_center_id="CC-001",
    vendor_name="BlueSky Cloud Solutions",
    vendor_id="V-002",
    category="office_supplies",
    item_description="Standard office paper and toner",
    quantity=25,
    unit_price=50.00,
    total_amount=1250.00,
)

recommendation = recommend_procurement_action(req)
print(recommendation)