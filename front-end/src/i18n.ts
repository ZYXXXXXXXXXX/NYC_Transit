import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { Accessibility } from '@mui/icons-material';

const resources = {
  en: {
    translation: {
      appTitle: 'MetroDiver',
      transitMap: 'Transit Map',
      serviceStatus: 'Service Status',
      userCenter: 'User Center',
      login: 'Login',
      logout: 'Logout',
      notLoggedIn: 'Not logged in, please log in first',
      close: 'Close',
      line: 'Line',
      accessibility: 'Accessibility',
      schedule: 'Schedule',
      yes: 'Yes',
      no: 'No',
      noDepartures: 'No {{dir}} departures',
      departed: 'Departed',
      nextTrain: 'Next train in {{min}} min',
      accessibilityequi: 'Accessibility Equipment',
    },
  },
  zh: {
    translation: {
      appTitle: '地铁导航',
      transitMap: '线路图',
      serviceStatus: '服务状态',
      userCenter: '用户中心',
      login: '登录',
      logout: '登出',
      notLoggedIn: '未登录，请先登录',
      close: '关闭',
      line: '线路',
      accessibility: '无障碍',
      schedule: '时刻表',
      yes: '是',
      no: '否',
      noDepartures: '没有{{dir}}方向的列车',
      departed: '已发车',
      nextTrain: '下一班列车 {{min}} 分钟',
      accessibilityequi: '无障碍设施',
    },
  },
  es: {
    translation: {
      appTitle: 'MetroDiver',
      transitMap: 'Mapa',
      serviceStatus: 'Estado del servicio',
      userCenter: 'Centro de usuario',
      login: 'Iniciar sesión',
      logout: 'Cerrar sesión',
      notLoggedIn: 'No ha iniciado sesión',
      close: 'Cerrar',
      line: 'Línea',
      accessibility: 'Accesibilidad',
      schedule: 'Horario',
      yes: 'Sí',
      no: 'No',
      noDepartures: 'Sin salidas hacia {{dir}}',
      departed: 'Partido',
      nextTrain: 'Próximo tren en {{min}} min',
      accessibilityequi:'Equipo de accesibilidad',
    },
  },
};

i18n
  .use(LanguageDetector)          // detects browser / saved choice
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  });

export default i18n;
