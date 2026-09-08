from backend.app.tools.order_tools import get_order
from backend.app.tools.customer_tools import get_customer
from backend.app.tools.cancellation_tools import cancel_order
from backend.app.tools.ticket_tools import create_ticket
from backend.app.tools.refund_tools import request_refund
from backend.app.tools.knowledge_tools import search_knowledge_base


AVAILABLE_TOOLS = [
    get_order,
    get_customer,
    cancel_order,
    create_ticket,
    request_refund,
    search_knowledge_base,
]