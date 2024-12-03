from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from api.v1.common import app_login
from api.v1.user_panel import app_patient, app_type_research, app_user, app_desyncdata, app_device, app_clinic_user, app_sse
from api.v1.admin_panel import app_clinic, app_device_type, app_admin_panel, app_user_admin, app_patient_admin, \
    app_device_admin, app_desyncdata_admin, app_clinic_address, app_type_research_admin, app_settings

from config.settings import settings


app = FastAPI(
    title=f"Read-only API для: {settings.project_name}",
    description="Сервис для выявления десинхронизации в процессе реабилитации",
    version="1.0.0",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

# @app.on_event("startup")
# async def on_startup():
#     # Initialize cache
#     FastAPICache.init(InMemoryBackend())

app.include_router(app_login.router)

app.include_router(app_admin_panel.router)
app.include_router(app_clinic.router)
app.include_router(app_clinic_address.router)
app.include_router(app_desyncdata_admin.router)
app.include_router(app_device_admin.router)
app.include_router(app_device_type.router)
app.include_router(app_patient_admin.router)
app.include_router(app_user_admin.router)
app.include_router(app_type_research_admin.router)
app.include_router(app_settings.router)

app.include_router(app_desyncdata.router)
app.include_router(app_device.router)
app.include_router(app_patient.router)
app.include_router(app_type_research.router)
app.include_router(app_user.router)
app.include_router(app_sse.router)
app.include_router(app_clinic_user.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
