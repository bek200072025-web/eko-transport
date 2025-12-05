from fastapi import HTTPException


def role_verification(user, function: str):
    """
    Foydalanuvchining funksiyani bajarishga ruxsati bor-yo‘qligini tekshiradi.
    :param user: Hozirgi foydalanuvchi obyekti
    :param function: Bajarilayotgan funksiya nomi
    :raises HTTPException: Agar ruxsat bo'lmasa, 401 xato qaytaradi
    """
    allowed_functions_for_admins = {}

    if user.role == 'boss':
        return True

    if user.role == 'admin' and function not in allowed_functions_for_admins:
        return True

    raise HTTPException(status_code=401, detail="Sizga ushbu amalni bajarishga ruxsat berilmagan!")
