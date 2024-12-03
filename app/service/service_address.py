# from http import HTTPStatus
# from fastapi import HTTPException
# # from sqlalchemy.future import select
# from sqlalchemy import update, select, delete
#
# from db.postgres import get_session, AsyncSession
# from models.clinicaddress import ClinicAddress, ClinicAddressRead, ClinicAddressCreate
# from etl.main import terminate_start_process
#
#
# async def create_clinic(data: ClinicAddressCreate, session: AsyncSession) -> ClinicAddress:
#     result = ClinicAddress.from_orm(data)
#     try:
#         session.add(result)
#         await session.commit()
#         await session.refresh(result)
#         return result
#     except HTTPException:
#         raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Data not write into DB')
#
#
# async def get_all(session: AsyncSession) -> list[ClinicAddress]:
#     result = await session.execute(select(ClinicAddress))
#     clinic_address = result.scalars().all()
#     return clinic_address
#
#
# async def read_clinic_address(uuid, session: AsyncSession) -> ClinicAddress:
#     result = await session.execute(select(ClinicAddress).filter(ClinicAddress.id == uuid))
#     clinic_address = result.first()
#     return clinic_address[0]
#
#
# async def update_clinic_address(uuid, session: AsyncSession, data: ClinicAddressCreate | dict):
#     try:
#         await session.execute(update(ClinicAddress).where(ClinicAddress.id == uuid).values(data.dict()))
#         await session.commit()
#         return ClinicAddressRead.from_orm(data)
#     except HTTPException as he:
#         raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Updating error - {he}')
#
#
# async def delete_clinic_address(uuid, session: AsyncSession):
#     try:
#         result = await session.execute(delete(ClinicAddress).where(ClinicAddress.id == uuid))
#         await session.commit()
#         return result
#     except HTTPException as e:
#         raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Deleting error - {e.message}')
#
#
# async def start_stop_process(uuid: int, status: bool, session: AsyncSession):
#     clinic_name = await get_address_name(device_id=uuid, session=session)
#     try:
#         clinic_address = terminate_start_process(clinic_name, status)
#         result = await update_clinic_address(uuid=uuid, session=session, data={'status': status})
#         return HTTPStatus.OK
#     except HTTPException as e:
#         raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Start/stop device error - {e.message}')
#
#
# async def get_address_name(clinic_address_id, session: AsyncSession):
#     result = await session.execute(select(ClinicAddress).filter(ClinicAddress.id == clinic_address_id))
#     clinic_address = result.fetchone()
#     return dict(*clinic_address).get('name')