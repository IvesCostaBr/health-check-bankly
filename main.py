import requests
from datetime import datetime
from fastapi import FastAPI


def validate_status_service():
    """Validate state of service."""
    try:
        datetme_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response = requests.get(
            "https://status.bankly.com.br/api/v2/incidents/unresolved.json"
        )
        data = response.json()

        incident_not_solved = list(
            filter(lambda x: not x.get("resolved_at"), data.get("incidents"))
        )
        if not len(incident_not_solved):
            return {"pix_status": True, "datetme": datetme_now}

        incident_critical = list(filter(
            lambda x: "autenticação" in x.get('name').lower(), incident_not_solved))
        if incident_critical:
            return {"pix_status": False, "datetme": datetme_now}

        list_errors_not_pass = ["incoming", "instant", "dict"]
        found_pix_erro_last_status = list(
            filter(
                lambda x: "pix" in x.get("name").lower()
                and x.get("new_status") != "operational",
                incident_not_solved[0]
                .get("incident_updates")[0]
                .get("affected_components"),
            )
        )
        if not len(found_pix_erro_last_status):
            return {"pix_status": True, "datetme": datetme_now}

        cant_stop = []
        for state in list_errors_not_pass:
            cant_stop += list(
                filter(
                    lambda x: state in x.get(
                        "name").lower(), found_pix_erro_last_status
                )
            )

        if len(cant_stop) > 0:
            return {"pix_status": False, "datetme": datetme_now}
        return {"pix_status": True, "datetme": datetme_now}
    except:
        return {"error": "error in process bankly status"}


app = FastAPI(title="Healthcheck Service")


@app.get("/bankly/status")
def get_status_bankly():
    return validate_status_service()
