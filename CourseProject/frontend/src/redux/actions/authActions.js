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
      const pk = data?.pk?.[0]?.id ?? data?.pk?.id ?? data?.pk;
      const isSuperuser = data?.is_superuser?.[0]?.is_superuser ?? data?.is_superuser;
      localStorage.setItem('pk', String(pk));
      localStorage.setItem('is_superuser', String(isSuperuser));

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
