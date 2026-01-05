import Cookies from 'js-cookie';
import { loginRequest, loginSuccess, loginFailure } from '../reducers/authReducer.js';

export const login = (credentials) => async (dispatch) => {
  try {
    dispatch(loginRequest());

    const csrftoken = Cookies.get('csrftoken');

    if (!csrftoken) {
      throw new Error('Ошибка аутентификации. Пожалуйста, обновите страницу.');
    }

    const response = await fetch('http://localhost:8002/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
        'Accept': 'application/json'
      },
      body: JSON.stringify(credentials),
      credentials: 'include'
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.clear();
      const pkRaw = data?.pk;
      const isSuperuserRaw = data?.is_superuser;

      const pk =
        pkRaw?.[0]?.id ??
        pkRaw?.[0]?.pk ??
        (pkRaw?.[0] && typeof pkRaw?.[0] === 'object' ? Object.values(pkRaw[0])[0] : undefined) ??
        pkRaw?.id ??
        pkRaw?.pk ??
        pkRaw;

      const isSuperuser =
        isSuperuserRaw?.[0]?.is_superuser ??
        isSuperuserRaw?.[0]?.isSuperuser ??
        (isSuperuserRaw?.[0] && typeof isSuperuserRaw?.[0] === 'object'
          ? Object.values(isSuperuserRaw[0])[0]
          : undefined) ??
        isSuperuserRaw?.is_superuser ??
        isSuperuserRaw?.isSuperuser ??
        isSuperuserRaw;

      if (pk === undefined || pk === null || pk === '' || pk === 'undefined') {
        throw new Error('Ошибка аутентификации: сервер не вернул идентификатор пользователя (pk).');
      }
      localStorage.setItem('pk', String(pk));
      localStorage.setItem('is_superuser', String(!!isSuperuser));

      dispatch(loginSuccess({
        user: data.email,
        token: data.token
      }));

      return data;
    } else {
      throw new Error(data.detail || 'Не удалось войти. Пожалуйста, проверьте ваши учетные данные.');
    }
  } catch (error) {
    dispatch(loginFailure(error.message));
    throw error;
  }
};
