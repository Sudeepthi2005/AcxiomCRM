from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Customer, Lead, Opportunity
from ..utils import audit

api_bp=Blueprint("api",__name__,url_prefix="/api")

def customer_json(c):
    return {"id":c.id,"customer_code":c.customer_code,"customer_name":c.customer_name,"email":c.email,"phone":c.phone,"company_name":c.company_name,"status":c.status}

@api_bp.route("/customers",methods=["GET","POST"])
@login_required
def customers():
    if request.method=="GET":
        query=Customer.query
        if current_user.role_name=="Sales Executive": query=query.filter_by(created_by=current_user.id)
        q=request.args.get("q")
        if q: query=query.filter(Customer.customer_name.ilike(f"%{q}%"))
        return jsonify({"success":True,"data":[customer_json(c) for c in query.all()]})
    data=request.get_json(silent=True) or {}
    name=str(data.get("customer_name","")).strip()
    email=str(data.get("email","")).strip().lower()
    phone=str(data.get("phone","")).strip()
    if not name or "@" not in email or len(phone)!=10 or not phone.isdigit():
        return jsonify({"success":False,"error":"Invalid customer data"}),400
    if Customer.query.filter((Customer.email==email)|(Customer.phone==phone)).first():
        return jsonify({"success":False,"error":"Duplicate email or phone"}),409
    c=Customer(customer_code=f"CUST-{Customer.query.count()+1:04d}",customer_name=name,email=email,phone=phone,
        company_name=data.get("company_name"),status=data.get("status","Active"),created_by=current_user.id)
    db.session.add(c); db.session.commit(); audit("API_CREATE","Customer",c.id)
    return jsonify({"success":True,"data":customer_json(c)}),201

@api_bp.route("/customers/<int:id>",methods=["GET","PUT","DELETE"])
@login_required
def customer_detail(id):
    c=Customer.query.get_or_404(id)
    if request.method=="GET": return jsonify({"success":True,"data":customer_json(c)})
    if current_user.role_name=="Sales Executive" and c.created_by!=current_user.id: return jsonify({"success":False,"error":"Forbidden"}),403
    if request.method=="DELETE":
        if current_user.role_name!="Admin": return jsonify({"success":False,"error":"Forbidden"}),403
        c.status="Inactive"; db.session.commit(); audit("API_DELETE","Customer",c.id)
        return jsonify({"success":True,"message":"Customer deactivated"})
    data=request.get_json(silent=True) or {}
    c.customer_name=str(data.get("customer_name",c.customer_name)).strip()
    c.email=str(data.get("email",c.email)).strip().lower()
    c.phone=str(data.get("phone",c.phone)).strip()
    db.session.commit(); audit("API_UPDATE","Customer",c.id)
    return jsonify({"success":True,"data":customer_json(c)})

@api_bp.route("/leads",methods=["GET","POST"])
@login_required
def leads():
    if request.method=="GET":
        query=Lead.query
        if current_user.role_name=="Sales Executive": query=query.filter_by(assigned_to=current_user.id)
        return jsonify({"success":True,"data":[{"id":x.id,"lead_code":x.lead_code,"lead_name":x.lead_name,"status":x.status,"expected_value":x.expected_value} for x in query.all()]})
    data=request.get_json(silent=True) or {}
    name=str(data.get("lead_name","")).strip()
    if not name: return jsonify({"success":False,"error":"lead_name is required"}),400
    l=Lead(lead_code=f"LEAD-{Lead.query.count()+1:04d}",lead_name=name,email=data.get("email"),phone=data.get("phone"),
        company_name=data.get("company_name"),source=data.get("source","API"),status=data.get("status","New"),
        expected_value=float(data.get("expected_value",0)),assigned_to=current_user.id)
    db.session.add(l); db.session.commit(); audit("API_CREATE","Lead",l.id)
    return jsonify({"success":True,"data":{"id":l.id,"lead_name":l.lead_name}}),201

@api_bp.route("/opportunities",methods=["GET","POST"])
@login_required
def opportunities():
    if request.method=="GET":
        query=Opportunity.query
        if current_user.role_name=="Sales Executive": query=query.filter_by(assigned_to=current_user.id)
        return jsonify({"success":True,"data":[{"id":x.id,"name":x.opportunity_name,"amount":x.amount,"stage":x.stage,"probability":x.probability,"weighted_value":x.weighted_value} for x in query.all()]})
    return jsonify({"success":False,"error":"Use the web form for opportunity creation so business validation is applied."}),400
