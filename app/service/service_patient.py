# from http import HTTPStatus
# from fastapi import HTTPException
# # from sqlalchemy.future import select
# from sqlalchemy import update, select, delete
#
# from app.db.postgres import get_session, AsyncSession
# from app.models.patient import Patient, PatientRead, PatientCreate
# from etl.main import terminate_start_process
#
#
# async def create_patient(data: PatientCreate, session: AsyncSession) -> Patient:
#     result = Patient.from_orm(data)
#     try:
#         session.add(result)
#         await session.commit()
#         await session.refresh(result)
#         return result
#     except HTTPException:
#         raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Data not write into DB')
#
#
# async def get_all(session: AsyncSession) -> list[Patient]:
#     result = await session.execute(select(Patient))
#     patient = result.scalars().all()
#     return patient
#
#
# async def read_patient(uuid, session: AsyncSession) -> Patient:
#     result = await session.execute(select(Patient).filter(Patient.id == uuid))
#     patient = result.first()
#     return patient[0]
#
#
# async def update_patient(uuid, session: AsyncSession, data: PatientCreate | dict):
#     try:
#         await session.execute(update(Patient).where(Patient.id == uuid).values(data.dict()))
#         await session.commit()
#         return PatientRead.from_orm(data)
#     except HTTPException as he:
#         raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Updating error - {he}')
#
#
# async def delete_patient(uuid, session: AsyncSession):
#     try:
#         result = await session.execute(delete(Patient).where(Patient.id == uuid))
#         await session.commit()
#         return result
#     except HTTPException as e:
#         raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Deleting error - {e.message}')
#
#
# async def start_stop_process(uuid: int, status: bool, session: AsyncSession):
#     clinic_name = await get_patient_name(device_id=uuid, session=session)
#     try:
#         update_patient = terminate_start_process(clinic_name, status)
#         result = await update_patient(uuid=uuid, session=session, data={'status': status})
#         return HTTPStatus.OK
#     except HTTPException as e:
#         raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Start/stop device error - {e.message}')
#
#
# async def get_patient_name(patient_id, session: AsyncSession):
#     result = await session.execute(select(Patient).filter(Patient.id == patient_id))
#     patient = result.fetchone()
#     return dict(*patient).get('name')