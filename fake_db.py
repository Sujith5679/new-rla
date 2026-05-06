def load_fake_db():
    return {
        "POL12345": {
            "name": "Mr. Smith",
            "email": "smith@email.com",
            "status": "No Claim",
            "claim_id": None,
            "documents": None,
            "analysis": None,
        },

        "POL67890": {
            "name": "John Doe",
            "email": "john@email.com",
            "status": "Approved",
            "claim_id": "CLM2001",
            "analysis": "Fractured arm. Rest: 4 weeks. All documents valid.",
        },

        "POL11111": {
            "name": "Jane Roe",
            "email": "jane@email.com",
            "status": "Rejected",
            "claim_id": "CLM2002",
            "analysis": "Insufficient medical proof. Missing diagnosis report.",
        },

        "POL22222": {
            "name": "Arjun Kumar",
            "email": "arjun@email.com",
            "status": "Pending",
            "claim_id": "CLM2003",
            "analysis": "Back pain injury. Suggested rest: 2 weeks. Awaiting verification.",
        },

        "POL33333": {
            "name": "Priya Sharma",
            "email": "priya@email.com",
            "status": "Approved",
            "claim_id": "CLM2004",
            "analysis": "Surgery recovery case. Rest: 6 weeks. Approved after review.",
        },

        "POL44444": {
            "name": "Rahul Verma",
            "email": "rahul@email.com",
            "status": "Rejected",
            "claim_id": "CLM2005",
            "analysis": "Claim does not fall under policy coverage.",
        },

        "POL55555": {
            "name": "Sneha Iyer",
            "email": "sneha@email.com",
            "status": "Pending",
            "claim_id": "CLM2006",
            "analysis": "Migraine-related leave. Needs neurologist report.",
        },

        "POL66666": {
            "name": "Vikram Singh",
            "email": "vikram@email.com",
            "status": "No Claim",
            "claim_id": None,
            "documents": None,
            "analysis": None,
        },

        "POL77777": {
            "name": "Ananya Das",
            "email": "ananya@email.com",
            "status": "Approved",
            "claim_id": "CLM2007",
            "analysis": "Knee injury. Rest: 3 weeks. Documents verified.",
        },

        "POL88888": {
            "name": "Karthik R",
            "email": "karthik@email.com",
            "status": "Pending",
            "claim_id": "CLM2008",
            "analysis": "Work-related stress leave. Awaiting HR validation.",
        }
    }