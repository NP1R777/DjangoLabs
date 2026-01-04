import axios from 'axios';
import '../styles/ProfilePage.css';
import Header from '../components/Header.jsx';
import { useNavigate } from 'react-router-dom';
import React, { useState, useEffect } from 'react';

const ProfilePage = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});

  // Загрузка данных пользователя
  useEffect(() => {
    const pk = localStorage.getItem('pk');
    if (!pk) {
      navigate('/login');
      return;
    }

    const fetchUserData = async () => {
      try {
        const response = await axios.get(`http://localhost:8002/user-detail/${pk}/`);
        setUserData(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Ошибка при загрузке данных пользователя:', error);
        setLoading(false);
      }
    };

    fetchUserData();
  }, [navigate]);

  // Обработчик выхода из аккаунта
  const handleLogout = () => {
    axios.post('http://localhost:8002/logout/')
    localStorage.clear();
    navigate('/');
  };

  // Обработчик изменений в форме
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Очищаем ошибки при изменении
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  // Обработчик сохранения изменений
  const handleSaveChanges = async () => {
    // Валидация
    const newErrors = {};
    if (!formData.email) newErrors.email = 'Email обязателен';
    if (formData.password && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Пароли не совпадают';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    try {
      const pk = localStorage.getItem('pk');
      const updateData = {
        email: formData.email,
        password: formData.password || undefined
      };
      
      await axios.patch(`http://localhost:8002/user-detail/${pk}/`, updateData);
      
      alert('Данные успешно обновлены!');
      setShowEditModal(false);
      
      // Обновляем данные пользователя
      const response = await axios.get(`http://localhost:8002/user-detail/${pk}/`);
      setUserData(response.data);
    } catch (error) {
      console.error('Ошибка при обновлении данных:', error);
      alert('Произошла ошибка при обновлении данных');
    }
  };

  // Открытие модального окна редактирования
  const handleEditClick = () => {
    setFormData({
      email: userData.email,
      password: '',
      confirmPassword: ''
    });
    setErrors({});
    setShowEditModal(true);
  };

  if (loading) {
    return (
      <div className="profile-loading-container">
        <div className="profile-loading-spinner"></div>
      </div>
    );
  }

  return (
    <div>
        <Header />
        <div className="profile-container">
        <div className="profile-header">
            <h1>Личный кабинет</h1>
            <button className="profile-logout-button" onClick={handleLogout}>
            Выйти из аккаунта
            </button>
        </div>
        
        <div className="profile-card">
            <div className="profile-info">
            <div className="profile-info-item">
                <span className="profile-info-label">Email:</span>
                <span className="profile-info-value">{userData.email}</span>
            </div>
            
            <div className="profile-info-item">
                <span className="profile-info-label">Статус:</span>
                <span className="profile-info-value">
                {userData.is_superuser ? 'Администратор' : 'Пользователь'}
                </span>
            </div>
            </div>
            
            <button 
            className="profile-edit-button"
            onClick={handleEditClick}
            >
            Редактировать данные
            </button>
        </div>
        
        {/* Модальное окно редактирования */}
        {showEditModal && (
            <div className="profile-modal-overlay">
            <div className="profile-modal-content">
                <button 
                className="profile-modal-close"
                onClick={() => setShowEditModal(false)}
                >
                &times;
                </button>
                
                <h2>Редактирование профиля</h2>
                
                <form className="profile-edit-form">
                <div className="profile-form-group">
                    <label>Email *</label>
                    <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className={`profile-form-input ${errors.email ? 'input-error' : ''}`}
                    />
                    {errors.email && <div className="profile-error">{errors.email}</div>}
                </div>
                
                <div className="profile-form-group">
                    <label>Новый пароль</label>
                    <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="profile-form-input"
                    placeholder="Оставьте пустым, чтобы не менять"
                    />
                </div>
                
                <div className="profile-form-group">
                    <label>Подтвердите пароль</label>
                    <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className={`profile-form-input ${errors.confirmPassword ? 'input-error' : ''}`}
                    />
                    {errors.confirmPassword && (
                    <div className="profile-error">{errors.confirmPassword}</div>
                    )}
                </div>
                
                <div className="profile-form-actions">
                    <button 
                    type="button"
                    className="profile-save-button"
                    onClick={handleSaveChanges}
                    >
                    Сохранить изменения
                    </button>
                    <button 
                    type="button"
                    className="profile-cancel-button"
                    onClick={() => setShowEditModal(false)}
                    >
                    Отмена
                    </button>
                </div>
                </form>
            </div>
            </div>
        )}
        </div>
    </div>
  );
};

export default ProfilePage;